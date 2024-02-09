import os
import requests
import json
import pandas as pd
from typing import *
from modules.data_collection import DataCollection

class KotraMarketDataClient(DataCollection):
    """코트라 트라이빅의 품목별 유망시장 페이지에서 hscode를 기준으로 수출대상 물품의 유망시장 정보를 가져오는 코드

    How:
    1. 조회하고 싶은 hscode를 입력
    2. 코트라 트라이빅의 픔목별 유망시장 페이지에서 수출입 통계, 유망국가, 인콰이어리, 전시회, 뉴스 등 종합적인 지표 가져옴
    3. 해당 데이터를 json, csv형태로 저장한다.

    """
    
    SAVE_DIR = os.path.join('output', 'kotra', 'market')
    BASE_URL = 'https://www.kotra.or.kr/bigdata/bhrcMarket'

    def __init__(self):
        if not os.path.exists(KotraMarketDataClient.SAVE_DIR): # 폴더가 따로 없을 시, 만들어 줌
            os.makedirs(os.path.join(KotraMarketDataClient.SAVE_DIR, 'json'))
            os.makedirs(os.path.join(KotraMarketDataClient.SAVE_DIR, 'csv'))
        self.market_info: Dict[str, Union[str, List]] = None
        self.market_info_keys: List[str] = None

    @classmethod
    def request(cls, url: str) -> requests.Response:
        """(추상 메서드 오버라이딩) 데이터 요청하는 메서드"""
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"요청에 실패햐였습니다 (에러코드 :{response.status_code})")

    @classmethod
    def parse(cls, data: Dict, key: str) -> Dict[str, Union[str, List]]:
        """(추상 메서드 오버라이딩)데이터를 따로 파싱하는 메서드"""
        if data is None:
            raise Exception(f"현재 파싱할 데이터가 존재하지 않습니다.")
        return {
            "code": data['code'],
            key: data.get(key, [])
        }

    @classmethod
    def save_data(cls, data: Dict, key: str=None, file_type: str='json') -> None:
        """(추상 메서드 오버라이딩)파싱한 데이터를 저장하는 메서드"""
        # key가 안들어오면 기본키
        if key == None:
            key = list(data.keys())[1]
        # key에서 가져오는 데이터가 list가 아닐 경우 => 무시(ex. baseYr)
        if not isinstance(data[key], list):
            return;
        
        hs_code = data['code']
        # csv파일 형식 저장
        if file_type == "csv":
            df = pd.json_normalize(data, key, ['code'])
            if len(df) == 0:
                df = pd.DataFrame({"code": data["code"]}, index=[0]); # 데이터가 하나도 없을 경우 대비하여
            else:
                df = df[['code'] + [col for col in df.columns if col != 'code']]
            save_path = os.path.join(cls.SAVE_DIR, 'csv', f'{hs_code}', f'{hs_code}_{key}.json')
            os.makedirs(os.path.dirname(save_path), exist_ok=True) # 없을 경우 디렉토리 생성해주고 있으면 예외 일으키지 않고 넘어감
            df.to_csv(save_path, index=False, encoding='utf-8')
            return
        
        # json파일 형식 저장
        if file_type == "json":
            save_path = os.path.join(cls.SAVE_DIR, 'json', f'{hs_code}', f'{hs_code}_{key}.json')
            os.makedirs(os.path.dirname(save_path), exist_ok=True) # 없을 경우 디렉토리 생성해주고 있으면 예외 일으키지 않고 넘어감
            with open(save_path, 'w', encoding='utf-8') as json_file:
                json.dump({"code": data["code"], "data": data[key]}, json_file, ensure_ascii=False, indent=4)
            return

        raise Exception(f"타입 오류")
    
    def save_bulk_data(self, file_type: str='json') -> None:
        """market_info에 있는 모든 정보를 json으로 한번에 저장"""
        if self.market_info == None:
            raise Exception("데이터가 하나도 없습니다.")
        if file_type != "json":
            raise Exception("현재 지원하지 않는 확장자입니다.")
            
        hs_code = self.market_info['code']
        save_path = os.path.join(KotraMarketDataClient.SAVE_DIR, 'json', f'{hs_code}', f'{hs_code}_bulk.json')
        os.makedirs(os.path.dirname(save_path), exist_ok=True) # 없을 경우 디렉토리 생성해주고 있으면 예외 일으키지 않고 넘어감
        with open(save_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.market_info, json_file, ensure_ascii=False, indent=4)

    def save_all_data(self, file_type: str='json') -> None:
        """저장할 수 있는 모든 정보를 한번에 저장할 수 있도록 하는 메서드"""
        for key in self.market_info_keys:
            KotraMarketDataClient.save_data(self.market_info, key, file_type)

    def collect_market_data(self, hs_code: str) -> None:
        """코트라 트라이빅 > 품목별 유망시장 페이지에서 제공하는 모든 데이터 가져오는 메서드"""
        url = f"{KotraMarketDataClient.BASE_URL}/search?type=hscd&code={hs_code}"
        response = KotraMarketDataClient.request(url)
        self.market_info = response.json()
        self.market_info_keys = list(self.market_info.keys())[1:] # code는 제외
        
    def collect_hs_info(self, hs_code: str) -> Dict[str, Union[str, List]]:
        """품목명과 설명을 가져오는 메서드"""
        url = f"{KotraMarketDataClient.BASE_URL}/hsName?hsCode={hs_code}"
        response = KotraMarketDataClient.request(url)
        hs_name_dict = response.json()
        return hs_name_dict

    def parse_news_data(self) -> Dict[str, Union[str, List]]:
        """market data에서 news데이터만 따로 빼온다"""
        return KotraMarketDataClient.parse(self.market_info, 'knInfoList')

    def parse_export_trend_3year(self) -> Dict[str, Union[str, List]]:
        """market data에서 한국 3년치 수출 트렌드 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'kor3YearsExpTrendFirstList')

    def parse_world_market_export_rank(self) -> Dict[str, Union[str, List]]:
        """market data에서 세계시장 교역 수출 순위 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'worldMarketExpRankList')

    def parse_buying_offer(self) -> Dict[str, Union[str, List]]:
        """market data에서 인콰이어리 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'buyingOffer')

    def parse_exhibition_list(self) -> Dict[str, Union[str, List]]:
        """market data에서 상품 관련 전시회 정보 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'exbiInfoList')

    def parse_world_market_import_rank(self) -> Dict[str, Union[str, List]]:
        """market data에서 세계시장 교역 수입 순위 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'worldMarketImpRankList')

    def parse_import_export_sum(self) -> Dict[str, Union[str, List]]:
        """market data에서 세계시장 교역 수입 순위 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'impExpStatsSum')

    def parse_promising_list(self) -> Dict[str, Union[str, List]]:
        """market data에서 유망국가 추출"""
        return KotraMarketDataClient.parse(self.market_info, 'promisingCountryList')

    def parse_import_regulation_list(self) -> Dict[str, Union[str, List]]:
        """market data에서 수입규제 데이터 리스트"""
        return KotraMarketDataClient.parse(self.market_info, 'importReglInfoList')

    def parse_export_trend_data_second(self) -> Dict[str, Union[str, List]]:
        """market data에서 한국 3년치 수출 트렌드 추출(어떤 데이터인지 확인)"""
        return KotraMarketDataClient.parse(self.market_info, 'kor3YearsExpTrendSecondList')

    def parse_market_share_list(self) -> Dict[str, Union[str, List]]:
        """market data에서 국가별 해당 수출입 상품 점유율 정보"""
        return KotraMarketDataClient.parse(self.market_info, 'impExpMkshRateList')

    def parse_stat_list(self) -> Dict[str, Union[str, List]]:
        """market data에서 국가별 수출입 통계정보"""
        return KotraMarketDataClient.parse(self.market_info, 'impExpStatsList')

    def parse_export_trend_5year(self) -> Dict[str, Union[str, List]]:
        """market data에서 한국 5개년 수출리스트"""
        return KotraMarketDataClient.parse(self.market_info, 'kor5YearsExpsttList')
            
if __name__ == "__main__":
    client = KotraMarketDataClient()
    hs_code = '190230'  # 예시 HS Code
    # hs_code = '870830'
    client.collect_market_data(hs_code) # 코드라에 API요청해서 데이터 가져오기
    print("Success to collect data")
    
    client.save_bulk_data() # 전체 벌크 데이터 json으로 저장
    print("Complete saving bulk data")
    
    client.save_all_data(file_type='json') # 각 도메인별로 파일 각각 json으로 저장
    client.save_all_data(file_type='csv') # 각 도메인별로 파일 각각 csv파일로 저장
    print("Complete saving")
