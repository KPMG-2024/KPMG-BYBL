import os
import time
import json
import pandas as pd
import requests
from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
from bs4 import BeautifulSoup
from typing import *


class KsureBuyerClient():
    """
    hscode와 국가만 있으면 => 해당 국적 + 산업에 종사하는 바이어 리스트를 무보에서 추출

    How:
    1. 산업 코드 : hscode는 기본적으로 1 : N 관계
    바이어를 검색할 때, 분류 코드가 없어서 다음으로 넘어가지 못하는 현상 발생(ex. 중국-21101)
    """
    
    SAVE_DIR = os.path.join('output', 'ksure', 'buyer_list')
    BASE_URL = 'https://www.ksure.or.kr:8443/research/buyer/buyerView.do'
    
    def __init__(self, mapping_data: str = None) -> None:
        if not os.path.exists(KsureBuyerClient.SAVE_DIR): # 폴더가 따로 없을 시, 만들어 줌
            os.makedirs(os.path.join(KsureBuyerClient.SAVE_DIR, 'json'))
            os.makedirs(os.path.join(KsureBuyerClient.SAVE_DIR, 'csv'))
        if mapping_data == None:
            self.mapping_data_path = os.path.join("config", "base_data", "istans_hscd_info.csv") # 기본적인 주소
        else:
            self.mapping_data_path = mapping_data    
        self.options = None # 셀레니움 웹드라이버 설정
        self.driver = None # 셀레니움 웹드라이버
           
    @classmethod
    def save_data(cls, buyer_list: List, file_type: str='json') -> None:
        """(추상 메서드 오버라이딩)무보에서 가져온 바이어 리스트를 저장하는 메서드"""
        # 저장할 데이터가 아예 없는 경우
        if buyer_list[0]['PageVO']['totalCount'] < 1 :
            raise Exception("데이터가 없어 저장하지 않습니다")
        
        nation_name = buyer_list[0]['selectBuyerList'][0]['nation_name']
        industry_code = buyer_list[0]['selectBuyerList'][0]['industry_code']
        hscode = buyer_list[0]['selectBuyerList'][0]['hscode']
        
        # json으로 저장
        if file_type == 'json':
            file_name = f'{nation_name}_{hscode}.json'
            buyer_list2 = [buyer for page in buyer_list for buyer in page['selectBuyerList']]
            with open(os.path.join(cls.SAVE_DIR, 'json', file_name), 'w') as json_file:
                json.dump({"nation_name" : nation_name,
                           "industry_code": industry_code,
                           "hscode": hscode,
                           "data": buyer_list2}, json_file, ensure_ascii=False, indent=4)
            return

        # csv파일로 저장
        if file_type == 'csv':
            df = pd.json_normalize(buyer_list, 'selectBuyerList')
            file_name = f'{nation_name}_{hscode}.csv'
            df = df[['nation_name'] + ['industry_code'] + ['hscode'] + [col for col in df.columns if col != 'industry_code' or col != 'hscode' or col != 'nation_name']]
            df.to_csv(os.path.join(cls.SAVE_DIR, 'csv', file_name), index=False, encoding='utf-8')
            return
            
        raise Exception(f"타입 오류")
    
    @staticmethod
    def is_nation_exist(country: str) -> bool:
        nat_cd_dict = []
        path = os.path.join('config', 'base_data', 'ksure_nation_code_list.json')
        with open(path, 'r') as f:
            nat_cd_dict = json.load(f)['data']
        if nat_cd_dict.get(country) == None: # mapping되는 데이터가 없을 경우 exception발생
            raise Exception(f"입력하신 {country}는 존재하지 않습니다.")
        return nat_cd_dict[country]
    
    def get_industry_code(self, nation_name: str, hscode: str) -> str:
        """industry-hscode mapping 데이터와 사용자 입력으로 들어온 국가 및 hscode 활용해 industry code 추출"""
        mapping_industry_hscode = pd.read_csv(self.mapping_data_path);

        # industry 및 hscode는 정수이므로 앞 0이 소실될 수 있으므로 zfill()
        mapping_industry_hscode['industry_code'] = mapping_industry_hscode['industry_code'].apply(lambda x: str(x).zfill(5)) 
        mapping_industry_hscode['hscode'] = mapping_industry_hscode['hscode'].apply(lambda x: str(x).zfill(6))
    
        industry_code = mapping_industry_hscode[['industry_code','hscode']].set_index('hscode').to_dict()['industry_code'][hscode]
    
        return industry_code
    
    def start_selenium_driver(self, headless = True) -> None:
        self.options = webdriver.ChromeOptions()
        if headless == True:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox') # 보안 기능 비활성화 (샌드박스라는 공간을 비활성화 시킨다는 뜻)
        self.options.add_argument('--disable-dev-shm-usage') # /dev/shm(공유메모리) 디렉토리를 사용하지 않는다는 뜻
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=self.options)

    def collect_buyer(self, nation_name: str, industry_code: str, hscode: str) -> List[Dict]:
        if self.driver == None:
            self.start_selenium_driver()
        
        nation_name_ = nation_name # 국가 이름
        industry_code_ = industry_code # 산업 코드
        raw_data = {} # 스크레이핑해서 저장될 raw data
        
        self.driver.get(KsureBuyerClient.BASE_URL)
        time.sleep(5)

        # 1. 국가 검색창에 사용자가 입력한 국가 검색
        nationNm_element = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nationNm"))
        )
        
        # 2. 국가 이름 딕셔너리에 존재하는지 확인하기
        # if nation_name_ in [item['trgtpsnAbbrNm'] for item in KsureBuyerClient.NATION_LIST]:
        if self.is_nation_exist(nation_name_):
            print(f'국가 : {nation_name_}, 산업코드 : {industry_code_}에 대한 정보를 수집합니다.')    
            nationNm_element.send_keys(nation_name_)
        else:
            raise Exception(f"국가 이름이 존재하지 않습니다.")
        
        # 3. 바이어 검색
        ## 바이어명에 " "를 입력하면 왠만한 전체 바이어가 검색됨.
        ## 무보 플랫폼은 국가명 + 바이어명 or 국가명 + 산업명을 검색해야하는데 아마 실제 구현 시에는 국가명 + 산업명을 검색할 확률이 매우 높음.
        button = self.driver.find_element(By.CLASS_NAME, 'btn_type')
        button.click()
    
        # 4. 대분류 코드를 가져옴
        ## 산업 대분류로 매칭해서 엘레먼트를 찾아줘야함. 
        soup = BeautifulSoup(self.driver.find_element(By.CSS_SELECTOR, '#oneStep').get_attribute('innerHTML'), 'html.parser')
        for a in soup.find_all('a'):
            code = a['onclick'].split('"')[1]
            name = a['onclick'].split('"')[3]
            index_ = a['onclick'].split('"')[5]
            raw_data[code] = {"name": name, "index": index_}

        # 5. 입력으로 들어오는 코드들을 활용해 적절히 매칭해서 클릭
        if self.is_valid_code(industry_code_, raw_data) == False:
            raise Exception(f"{industry_code_}는 조회할 수 없는 번호여서, 검색을 중단합니다.")
        
        # 6. 검색 
        nationNm_element.send_keys(Keys.ENTER) # 아무 엘레먼트나 클릭해서 엔터키를 누르면 검색이 됨.
        time.sleep(2)
        try:
            # 첫 번째 바이어가 나타날 때까지 기다림. 만약 3초 안에 처리하면 바이어가 보통 0명인 경우라 잘 처리해주면 됨.
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#pagingId > a.current'))
            )

            # 바이어가 없으면 드라이버 종료
            if element.text == '0':
                print('바이어가 0건 입니다.')
                self.quit_selenium_driver()
                return

        except TimeoutException:
            # 예외가 발생하면 로딩이 오래 걸린다는 의미이므로 넉넉하게 시간을 다시 줌.
            print('로딩 중')
            element = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#buyerTbody > tr:nth-child(1) > td.t_l'))
            )

        # 7. 검색 결과 가져오기
        em_element = self.driver.find_element(By.CSS_SELECTOR, "span.board_total em") #  <em> 태그 안에 있는 내용은 총 n건의 검색 결과에서 n을 가져옴.
        result_text = em_element.text
        time.sleep(1)
        
        element = self.driver.find_element(By.CSS_SELECTOR, "#pagingId > a.btn_prev")
        element.click()
        total_page = round(int(result_text) / 10) # 총 클릭 페이지 계산

        for i in tqdm(range(total_page)):
            
            #다음 버튼 누르면서 계속 정보를 받아옴
            element = self.driver.find_element(By.CSS_SELECTOR, f"#pagingId > a.btn_next")
            element.click()
            time.sleep(2)
    
            # 100개마다 백업해줌.
            if i % 100 == 0:
                # Filter and print the specific request
                request_list= []
    
                for request in self.driver.requests:
                    if request.response and request.url == 'https://www.ksure.or.kr:8443/research/buyer/selectBuyerList.do':
                        # Print the response
                        json_response = request.response.body.decode('utf-8')
                        new_data = json.loads(json_response)
    
                        # Check for duplicates before adding to the list
                        if new_data not in request_list:
                            request_list.append(new_data)
                
                # 해당 국가명과 산업코드는 고유한 값으로 해주기 (혹시나 겹칠까봐, 키 이름 바꾸어도 괜찮음)
                for item in request_list:
                    for item2 in item['selectBuyerList']:
                        item2['nation_name'] = nation_name_
                        item2['industry_code'] = industry_code_
                        item2['hscode'] = hscode

                KsureBuyerClient.save_data(request_list);
                        

        # post된 정보를 다 가져옴
        request_list= []
    
        for request in self.driver.requests:
            # 바이어 리스트 관련 정보만 필터링
            if request.response and request.url == 'https://www.ksure.or.kr:8443/research/buyer/selectBuyerList.do':
                # Print the response
                # 리스폰스를 디코드해줘야지 정상적으로 나옴.
                json_response = request.response.body.decode('utf-8')
    
                new_data = json.loads(json_response)
                
                # Check for duplicates before adding to the list
                if new_data not in request_list:
                    request_list.append(new_data)
    
        # 해당 국가명과 산업코드는 고유한 값으로 해주기 (혹시나 겹칠까봐, 키 이름 바꾸어도 괜찮음)
        for item in request_list:
            for item2 in item['selectBuyerList']:
                item2['nation_name'] = nation_name_
                item2['industry_code'] = industry_code_
                item2['hscode'] = hscode

        # 드라이버 종료
        self.quit_selenium_driver()
        return request_list
    
    def quit_selenium_driver(self) -> None:
        """셀리니움 드라이버 가동 후 드라이버 종료"""
        if self.driver != None:
            self.driver.quit()
            self.driver = None
    
    def is_valid_code(self, industry_code: str, raw_data: Dict) -> bool:
        """산업 코드가 무보 바이어 검색창에서 검색 가능한지 check해주는 메서드"""
        industry_key = str(industry_code[:2])
        flag = False # 1차 ~ 4차 분류까지 검색에 유효한 산업코드인지 여부를 체크해주는 변수
        ## level 1
        level1 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//a[@onclick='clickFun2(\"{industry_key}\",\"{raw_data[industry_key]['name']}\",\"{raw_data[industry_key]['index']}\")']"))
            )
        level1.click()

        level2_code = str(industry_code[:3])
        level2 = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#twoStep'))
            )
        time.sleep(1)

        ## level 2
        for tag in level2.find_elements(By.TAG_NAME, "a"):
            onclick_value = tag.get_attribute("onclick")
            if level2_code in onclick_value:
                tag.click()
                flag = True
                break  # 원하는 링크를 찾았으므로 루프 종료
        if flag == False:
            return False
        
        ## level 3
        flag = False
        level3_code = str(industry_code[:4])
        level3 = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#threeStep'))
            )
        time.sleep(1)

        for tag in level3.find_elements(By.TAG_NAME, "a"):
            onclick_value = tag.get_attribute("onclick")
            if level3_code in onclick_value:
                tag.click()
                flag = True
                break  # 원하는 링크를 찾았으므로 루프 종료
        if flag == False:
            return False
        
        ## level 4
        flag = False
        level4_code = str(industry_code[:5])
        level4 = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#fourStep'))
            )
        time.sleep(1)

        for tag in level4.find_elements(By.TAG_NAME, "a"):
            onclick_value = tag.get_attribute("onclick")
            if level4_code in onclick_value:
                tag.click()
                flag = True
                break  # 원하는 링크를 찾았으므로 루프 종료
        time.sleep(0.5)
        if flag == False:
            return False
        
        return True
        

if __name__ == "__main__":

    nation_name = "일본"
    hscode = "070910"
    # nation_name = "중국"
    # hscode = "293610"
    buyer_list = None

    # 클라이언트 인스턴스 생성
    buyer_client = KsureBuyerClient()

    # 산업 코드 가져오기
    industry_code = buyer_client.get_industry_code(nation_name, hscode)
    print("산업코드 가져오기")

    # 무보에서 데이터 가져오기
    try:
        buyer_list = buyer_client.collect_buyer(nation_name, industry_code, hscode)
    except Exception as e:
        print(e)
        buyer_client.quit_selenium_driver()

    # 데이터 저장(결과가 하나라도 있을 경우)
    if buyer_list is not None:
        buyer_client.save_data(buyer_list, file_type='json') # json파일 저장하
        buyer_client.save_data(buyer_list, file_type='csv') # csv파일 저장
        print("저장 성공")

