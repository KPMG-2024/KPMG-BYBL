import os
import requests
import json
import pandas as pd
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone
from typing import *
from modules.data_collection import DataCollection

class KotraNewsClient(DataCollection):
    """

    How:
    1. 국가 이름을 기준으로 코트라 > 상품 산업 조회 항목에서 그 국가의 뉴스 및 트렌드를 조사한다.
    2. 사용자가 국가 이름을 입력하면 사전에 setting해둔, 입력 국가에 mapping되는 코드를 통해 특정 국가 검색 가능하도록 함(ex - 캐니다 : 124)
    3. 수집한 데이터는 각 국가별로 폴더를 생성해 json파일에 저장
    """
    
    SAVE_DIR = os.path.join('raw', 'kotra', 'news')
    BASE_URL = 'https://dream.kotra.or.kr/ajaxf/frNews/getKotraBoardList.do'
    CONTENT_URL = 'https://dream.kotra.or.kr/kotranews/cms/news/actionKotraBoardDownDetail.do?MENU_ID=170'
    
    def __init__(self):
        if not os.path.exists(KotraNewsClient.SAVE_DIR): # 폴더가 따로 없을 시, 만들어 줌
            os.makedirs(os.path.join(KotraNewsClient.SAVE_DIR, 'json'))
        self.news_data = None; # 뉴스 데이터 변수


    @classmethod
    def request(cls, url: str, data: Dict = None, method='GET') -> requests.Response:
        """(추상 메서드 오버라이딩) 데이터 요청하는 메서드"""
        if method == 'GET': # GET
            response = requests.get(url)
            return response
        
        if method == 'POST':
            response = requests.post(url, data=data) # 데이터를 얻기 위해서 해당 url에는 post요청을 해야 함
            if response.status_code == 200:
                return response
            else:
                raise Exception(f"요청에 실패햐였습니다 (에러코드 :{response.status_code})")
            
        raise Exception("올바르지 않은 요청 메소드입니다")
    
    @classmethod
    def parse(cls, data: str) -> Dict[str, Union[str, List]]:
        """(추상 메서드 오버라이딩)데이터를 따로 파싱하는 메서드"""
        if data is None:
            raise Exception(f"현재 파싱할 데이터가 존재하지 않습니다.")
        return json.loads(data)['data']['list']

    @classmethod
    def save_data(cls, data: List[Dict], file_type: str='json') -> None:
        """(추상 메서드 오버라이딩)파싱한 상품,산업 관련 데이터를 저장하는 메서드"""
        # 데이터 유효성 검사
        if not isinstance(data, list):
            raise Exception(f"데이터가 올바르지 않습니다.")

        country = data[0]['NAT'] # 국가 추출          
        # json파일 형식 저장
        if file_type == "json":
            save_path = os.path.join(cls.SAVE_DIR, 'json', f'{country}.json')
            os.makedirs(os.path.dirname(save_path), exist_ok=True) # 없을 경우 디렉토리 생성해주고 있으면 예외 일으키지 않고 넘어감
            with open(save_path, 'w', encoding='utf-8') as json_file:
                json.dump({"country": country,
                           "last_updated" : cls.get_current_time(),
                           "data": data}, json_file, ensure_ascii=False, indent=4)
            return

        raise Exception(f"타입 오류")

    @classmethod
    def parse_html_content(cls, html_content: str) -> str:
        """html 형식의 데이터를 저장하기 용이하도록 처리, 파싱하는 메소드"""
        # BeautifulSoup로 HTML 파싱
        soup = BeautifulSoup(html_content, 'html.parser')

        # 모든 테이블을 찾아서 Markdown 형태로 변환하고 원래 위치에 삽입
        for table in soup.find_all('table'):
            # Pandas를 사용하여 HTML 테이블을 읽고 Markdown으로 변환
            markdown = pd.read_html(str(table), encoding='utf-8', header=0)[0].to_markdown(index=False)
            
            # Markdown 텍스트를 포함하는 새로운 <p> 태그 생성
            new_tag = soup.new_tag("p")
            new_tag.string = markdown
            
            # 원본 테이블을 새로운 <p> 태그로 교체
            table.replace_with(new_tag)

        # 모든 <p> 요소를 찾아 텍스트를 합치기
        combined_text = ''
        for element in soup.find_all():
            if element.name == 'p' and element.name != 'table':
                combined_text += element.get_text() + '\n'
            elif element.name == 'table':
                # 테이블이 발견되면 Pandas를 사용하여 테이블을 읽고 텍스트로 변환하여 추가
                table_text = pd.read_html(str(element), encoding='utf-8', header=0)[0].to_markdown(index=False)
                combined_text += table_text + '\n'
        
        return combined_text
    
    @staticmethod
    def get_current_time() -> str:
        """한국 시간을 가져오는 메서드"""
        return datetime.now(timezone('Asia/Seoul')).isoformat()
    
    @staticmethod
    def search_nat_cd(country: str) -> str:
        """국가 이름 입력하면 해당 국가 고유번호 반환하는 메서드"""
        nat_cd_dict = {}
        # 사전에 저장해 둔, 국가와 kotra 국가 고유 번호 mapping한 json파일 로드
        path = os.path.join('config', 'base_data', 'nation_code_list.json')
        with open(path, mode='r') as f:
            nat_cd_dict = json.load(f)
        
        if nat_cd_dict.get(country) == None: # mapping되는 데이터가 없을 경우 exception발생
            raise Exception(f"입력하신 {country}는 존재하지 않습니다.")
        return nat_cd_dict[country]
     
    def collect_news_data(self, country: str, data_per_page: int = 10) -> List[Dict]:
        """코트라 트라이빅의 뉴스 데이터 수집 메서드"""
        # post에 보낼 데이터 정보
        data = {
            'pageNo': 1,
            'pagePerCnt': 10,
            'SITE_NO': 3,
            'MENU_ID': 170,
            'CONTENTS_NO': 1,
            #bbs 관련 파라미터는 꼭 넣어야함.
            'bbsGbn': '01',
            'bbsSn': '243,254,254,403,257',
            'pNttSn': '',
            #레코드는 굉장히 많이 요청할 수 있음
            'recordCountPerPage': 10,
            'viewType': '',
            'pNewsGbn': '',
            'pStartDt': '',
            'pEndDt': '',
            #검색어
            'sSearchVal': '',
            #리전
            'pRegnCd': '',
            #국가
            'pNatCd': '',
            #무역관
            'pKbcCd': '',
            #산업
            'pIndustCd': '',
            #hscode
            'pHsCode': '',
            'pHsCodeNm': '',
            'pHsCdType': ''
            }
        # 입력으로 들어온 국가에 mapping되는 고유번호가 없을 경우 종료
        try:
            data['pNatCd'] = KotraNewsClient.search_nat_cd(country) # 국가 설정
        except Exception as e:
            print(e)
            return
        
        data['recordCountPerPage'] = data_per_page # 한 페이지당 얼마나 데이터 보여줄 건지
        response = KotraNewsClient.request(KotraNewsClient.BASE_URL, data = data, method='POST') # 데이터 요청
        kotra_commodity_info = KotraNewsClient.parse(response.text) # 요청받은 데이터 파싱
        if (len(kotra_commodity_info) < 1) :
            raise Exception(f"데이터가 존재하지 않습니다.")  
        
        content_list = [] # 데이터 저장할 리스트 생성
        for item in tqdm(kotra_commodity_info):
            ntt_sn = item['NTT_SN']
            bbs_sn = item['BBS_SN']

            params = f'&pNttSn={ntt_sn}&bbsSn={bbs_sn}'
            url = KotraNewsClient.CONTENT_URL + params
            response = response = KotraNewsClient.request(url, method='GET') # 데이터 요청
            html_content = response.text
            
            try:
                parsed_text = KotraNewsClient.parse_html_content(html_content)
                item['content'] = parsed_text
                content_list.append(item)
                time.sleep(1.5)
            except:
                print("해당 데이터는 파싱 중 오류가 발생해 스킵합니다")
            

            
        return content_list
            
if __name__ == "__main__":
    news_client = KotraNewsClient()

    country = "프랑스" # 국가 가준으로 검색

    # 데이터가 없을 시 예외처리
    try:
        news_data = news_client.collect_news_data(country) # 상품 관련 뉴스 데이터 추출
        print("Success to collect data")
        news_client.save_data(news_data) # 불러온 데이터 저장
        print(f"Complete saving {country} data")

    except Exception as e:
        print("An error occurred:", e)
