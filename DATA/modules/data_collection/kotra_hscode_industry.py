import os
import requests
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Dict, List
from modules.data_collection import DataCollection

class HSCodeIndustryClient(DataCollection):
    """HSCode와 한국표준산업분류코드(KSIC)를 매칭시키고 매칭 정보를 저장하기 위한 클래스

    How:
    1. 산업분류코드를 로드함
    2. 그 후 산업통계 분석시스템(ISTANS)에 산업분류코드 대분류 기준으로 요청해 해당 코드와 일치하는 hscode를 가져옴
    3. 매칭 정보를 저장(type: json, csv)
    4. 해당 hscode에 대한 한글 설명을 추가하기 위해서는 코트라에 추가적으로 요청하여 해당 hscode에 대한 정보를 가져올 수 있는 기능 탑재

    """
    
    SAVE_DIR = os.path.join('config', 'base_data')  # 저장 공간
    INDUSTRY_DATA = "https://github.com/FinanceData/KSIC/raw/master/KSIC_10.csv.gz"  # 산업분류코드 데이터
    ISTANS_URL = "https://www.istans.or.kr/tree/IndustryRelationCode.jsp?s_dimid=ISTANS&d_dimid=HS96&s_value="
    HSCODE_URL = "https://www.kotra.or.kr/bigdata/bhrcMarket/hsName?hsCode="  # 코트라의 hscode 데이터

    def __init__(self) -> None:
        if not os.path.exists(self.SAVE_DIR):  # 폴더가 따로 없을 시, 만들어 줌
            os.makedirs(self.SAVE_DIR)
        if os.path.exists(os.path.join(self.SAVE_DIR, "istans_hscd_info.csv")): # 파일 존재할 시
            raise Exception
            

    @classmethod
    def request(cls, url: str) -> requests.Response:
        """(추상 메서드 오버라이딩) 데이터 요청하는 코드"""
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"요청에 실패햐였습니다 (에러코드 :{response.status_code})")

    @classmethod
    def parse(cls, html_content: str, industry_code: str) -> Dict[str, str]:
        """(추상 메서드 오버라이딩) html content를 파싱하는 코드"""
        soup = BeautifulSoup(html_content, "html.parser")

        try:
            result = {}  # 파싱 결과를 담을 딕셔너리
            result['industry_code'] = industry_code  # 산업코드 담기

            related_hs_codes = []  # 해당 산업코드와 관계있는 hscode 추출

            # OECD 무역코드 추출
            dd_content = soup.find_all('dd')[1].decode_contents()  # <dd> 태그 내용을 HTML 문자열로 추출
            code_descriptions = dd_content.split('<br/>') if '<br/>' in dd_content else dd_content.split('<br>')  # <br> 태그로 분리

            # 각 항목을 처리
            for item in code_descriptions:
                # 공백과 특수문자 제거
                cleaned_item = item.strip().replace('\xa0', ' ').replace('&amp;', '&')

                # 코드와 설명 분리
                # 마지막 괄호 ")" 위치를 찾아서 코드와 설명을 분리
                code_start_idx = cleaned_item.rfind('(') + 1
                code_end_idx = cleaned_item.rfind(')')

                if code_start_idx > 0 and code_end_idx > 0:
                    code = cleaned_item[code_start_idx:code_end_idx]
                    description = cleaned_item[:code_start_idx - 2]  # 괄호와 코드 번호 앞까지가 설명

                    # 결과 리스트에 추가
                    related_hs_codes.append({"code": code, "description": description.strip()})

            result['related_hs_codes'] = related_hs_codes
            return result

        # industry code와 일치하는 hs코드가 존재하지 않을 경우
        except Exception as e:
            pass

    @classmethod
    def save_data(cls, matching_data: List[Dict], file_type='json') -> None:
        """(추상 메서드 오버라이딩) 산업코드-hscode 매칭 데이터 저장"""
        # 저장 파일 형식이 json일 경우
        if file_type == 'json':
            with open(os.path.join(cls.SAVE_DIR, 'istans_hscd.json'), 'w') as json_file:
                json.dump(matching_data, json_file, ensure_ascii=False, indent=4)
            return

        # 저장 파일 형식이 csv인 경우 => 추가적인 한글 설명까지 추가해서 저장한다.
        if file_type == 'csv':
            results = []
            for item in matching_data:
                for hscode in item['related_hs_codes']:
                    result = {
                        'industry_code': item['industry_code'],
                        'hscode': hscode['code'],
                        'description': hscode['description']
                    }
                    results.append(result)

            hs_istans = pd.DataFrame(results).drop_duplicates(subset=['industry_code', 'hscode']).reset_index(drop=True)

            idx = 0;
            while(idx < len(hs_istans)):
                try:
                    hscode_info = cls.collect_hscode_info(hs_istans.loc[idx, 'hscode'])
                    hsName = hscode_info['hsName']  # hscode 이름
                    parentHsName = hscode_info['parentHsName']  # 상위 hscode 이름
                    hs_istans.loc[idx, 'hsName'] = hsName
                    hs_istans.loc[idx, 'parentHsName'] = parentHsName
                    time.sleep(0.2)
                    idx += 1
                    
                    if idx == 100:
                        print(f"{idx}개 수집완료")
                        time.sleep(2)
                except:
                    print("과도한 request요청으로 time sleep")
                    time.sleep(20)
            # for idx in tqdm(range(len(hs_istans))):
            #     # hscode에 대한 상세정보를 가져옴
            #     hscode_info = cls.collect_hscode_info(hs_istans.loc[idx, 'hscode'])
            #     hsName = hscode_info['hsName']  # hscode 이름
            #     parentHsName = hscode_info['parentHsName']  # 상위 hscode 이름
            #     hs_istans.loc[idx, 'hsName'] = hsName
            #     hs_istans.loc[idx, 'parentHsName'] = parentHsName
            #     # 과도한 request 방지
            #     if (idx % 50 == 0):
            #         time.sleep(2.5)
                
            # 저장
            hs_istans.to_csv(os.path.join(cls.SAVE_DIR, 'istans_hscd_info.csv'), index=False, encoding='utf-8')

    @classmethod
    def collect_hscode_info(cls, hscode: str) -> Dict[str, str]:
        """코트라에서 hscode에 대한 한글 정보를 가져오는 메소드"""
        url = cls.HSCODE_URL + hscode
        response = cls.request(url)
        hscode_info = json.loads(response.text)
        return hscode_info

    def load_ksic(self) -> pd.DataFrame:
        """외부 csv파일의 산업분류코드를 불러오는 코드"""
        df_ksic = pd.read_csv(self.INDUSTRY_DATA, dtype='str')
        mapping_dict = self.create_mapping()  # 대분류코드를 매핑하기 위한 코드

        ## 아래 코드는 dataframe의 정보를 채워주는 역할을 한다.
        df_ksic['Industy_code'] = df_ksic['Industy_code'].str.pad(width=5, side='right', fillchar='0')
        df_ksic['대분류_코드'] = df_ksic['Industy_code'].str[:2]
        df_ksic['산업_대분류'] = df_ksic['대분류_코드'].map(mapping_dict)
        df_ksic['Industy_name'] = df_ksic['Industy_name'].replace(' ', '', regex=True)
        return df_ksic

    def create_mapping(self) -> Dict[str, str]:
        """숫자 범위를 알파벳으로 매핑하는 메서드"""
        ranges = {
            "A": [(1, 3)],
            "B": [(5, 8)],
            "C": [(10, 34)],
            "D": [(35, 35)],
            "E": [(36, 39)],
            "F": [(41, 42)],
            "G": [(45, 47)],
            "H": [(49, 52)],
            "I": [(55, 56)],
            "J": [(58, 63)],
            "K": [(64, 66)],
            "L": [(68, 68)],
            "M": [(70, 73)],
            "N": [(74, 76)],
            "O": [(84, 84)],
            "P": [(85, 85)],
            "Q": [(86, 87)],
            "R": [(90, 91)],
            "S": [(94, 96)],
            "T": [(97, 98)],
            "U": [(99, 99)],
        }
        mapping = {}
        for letter, range_list in ranges.items():
            for start, end in range_list:
                for i in range(start, end + 1):
                    # 숫자를 2글자 문자열로 변환 (예: 1 -> '01')
                    mapping[f"{i:02}"] = letter
        return mapping

    def generate_matching_data(self, df_ksic: pd.DataFrame) -> List[Dict]:
        """ksic 데이터를 불러와 hscode-산업코드 매칭 데이터 생성"""
        matching_data = []  # hscode-산업코드 매칭 데이터 담을 리스트

        # 산업코드와 hscode 매칭시켜주는 작업 진행
        for idx in tqdm(range(len(df_ksic))):
            industry_code = df_ksic.loc[idx, 'Industy_code']  # 산업코드 추출
            industry_level1 = df_ksic.loc[idx, '산업_대분류']  # 산업 대분류 추출

            params = f"{industry_level1}${industry_code[:2]}${industry_code[:3]}${industry_code[:4]}${industry_code[:5]}"  # url 문자열 생성
            url = self.ISTANS_URL + params

            # 요청
            html_content = self.request(url).text
            # 파싱
            result = self.parse(html_content, industry_code)
            # 결과가 정상적으로 나왔을 경우, 데이터 더해줌
            if result is not None:
                matching_data.append(result)

            # 과도한 request 방지
            if (idx % 100 == 0):
                time.sleep(2)
        return matching_data


if __name__ == "__main__":
    hscodeGen = HSCodeIndustryClient()
     # 산업분류코드 데이터 가져오기
    ksic_df = hscodeGen.load_ksic()
    print("Success to load ksic")
    # 매칭 데이터 생성
    matching_data = hscodeGen.generate_matching_data(ksic_df)
    print("Complete generating matching data")
    # 데이터 저장
    hscodeGen.save_data(matching_data, file_type='json') 
    hscodeGen.save_data(matching_data, file_type='csv')
    print("Complete saving")
