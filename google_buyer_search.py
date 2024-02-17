import os
import pandas as pd 
import json
import requests
import time
import dotenv # 환경변수 프로젝트 단위로 불러오기
from typing import Dict, List
from modules.data_collection import DataCollection
dotenv_file = dotenv.find_dotenv('../config/.env')
dotenv.load_dotenv(dotenv_file)

class BuyerSearchClient(DataCollection):
    """구글 API를 활용해 구글 검색 기능 제공

    How:
    1. 무보에서 추출한 바이어 데이터를 바탕으로(ksure_buyer_list.py) 구글 검색을 한다.

    """
    # API에 사용될 키값 
    ## TODO: 향후 리팩토링 할 예정
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
    
    GOOGLE_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
    GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    SAVE_DIR = os.path.join('raw', 'google', 'buyer_info')
    Trash_Link = ["youtube"] # 검색 대상에서 제외되는 사이트
    def __init__(self) -> None:
        if not os.path.exists(BuyerSearchClient.SAVE_DIR):  # 폴더가 따로 없을 시, 만들어 줌
            os.makedirs(os.path.join(BuyerSearchClient.SAVE_DIR, 'json'))

    @classmethod
    def request(cls, url: str, params = None, data = Dict, method='GET') -> requests.Response:
        """(추상 메서드 오버라이딩) 데이터 요청하는 메서드"""
        if method == 'GET': # GET
            response = requests.get(url, params=params)
            return response
        
        elif method == 'POST':
            response = requests.post(url, params=params, data=data) # 데이터를 얻기 위해서 해당 url에는 post요청을 해야 함
        
        else:
            raise Exception("올바르지 않은 요청 메소드입니다")
        
        # 응답번호 검증
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"요청에 실패햐였습니다 (에러코드 :{response.status_code})")
            
    @classmethod
    # TODO: 리팩토링 필요
    def parse(cls):
        pass

    @classmethod
    def save_data(cls, buyer_list: List, file_type: str='json') -> None:
        """(추상 메서드 오버라이딩)기존 바이어 리스트 데이터에 구글 검색 결과 첨부한 사진"""
        
        nation_name = buyer_list['nation_name']
        hscode = buyer_list['hscode']
        
        # json으로 저장
        if file_type == 'json':
            file_name = f'{nation_name}_{hscode}_search.json'
            with open(os.path.join(cls.SAVE_DIR, 'json', file_name), 'w') as json_file:
                json.dump(buyer_list, json_file, ensure_ascii=False, indent=4)
            return
            
        raise Exception(f"타입 오류")
            
    def get_prompt(self, input: str, instruction: str) -> str:
        """프롬프트를 제작하는 메서드"""
        prompt = f"""
                    Instruction: {instruction}
                    text: "{input}"
                    JSON Output:
                    """
        return prompt  
        
    def load_buyer_data(self, file_name: str = None) -> List[Dict]:
        """구글 검색을 위해 바이어 정보 가져오는 메소드"""

        path = os.path.join('output', 'ksure', 'buyer_list', 'json', file_name) # json형식 바이어 리스트 로드\

        with open(path, 'r') as f:
            buyer_data = json.load(f)
            # buyer_data = buyer_json['data'] # json항목에서 data만 추출한다
        return buyer_data   



    def request_google_api(self, query: str, wanted_row: int) -> pd.DataFrame:
        """구글 검색 API에 요청하는 메소드"""
        query= query.replace("|","OR")
        #query += "-filetype:pdf"
        start_pages=[]
        row_count = 0 

        for i in range(1, wanted_row+1000, 10):
            start_pages.append(i)

        # 각 페이지마다 반복
        for start_page in start_pages:
            # &cr=countryUS &lr=lang_en 넣으면 국가, 언어 설정 가능
            url = BuyerSearchClient.GOOGLE_SEARCH_ENDPOINT
            params = {
                'key': BuyerSearchClient.GOOGLE_API_KEY,
                'cx': BuyerSearchClient.GOOGLE_SEARCH_ENGINE_ID,
                'q': query,
                'start': start_page
            }
            search_result = BuyerSearchClient.request(url=url,
                                                           params=params,
                                                           method='GET').json() # 구글 검색 결과 json파일로
            search_items = search_result.get("items")
            # 검색 결과를 Dataframe으로 저장하기 위함
            search_result_df= pd.DataFrame(columns=['Title','Link','Description','Concated_text'])

            try:
                for i, search_item in enumerate(search_items, start=1):
                    # extract the page url
                    link = search_item.get("link")
                    if any(trash in link for trash in BuyerSearchClient.Trash_Link):
                        pass
                    else: 
                        # 페이지 제목 얻기
                        title = search_item.get("title")
                        # 페이지 스니펫 얻기
                        descripiton = search_item.get("snippet")
                        concated_text = f"Title:{title}\nLink:{link}\nDescription:{descripiton}" # 각각의 정보를 concat
                        # 페이지 총 결과
                        search_result_df.loc[start_page + i] = [title,link,descripiton,concated_text] 
                        row_count += 1
                        # 요청한 데이터 갯수를 넘었다면, 바로 반환 
                        if (row_count >= wanted_row):
                            return search_result_df
                        
            except Exception as e:
                print('Error :', e)
                return search_result_df

        
        return search_result_df        
    
    def collect_buyer_search_info(self, file_name: str) -> Dict:
        """Client단에서 바이어 정보를 요청하는 메소드"""
        buyer_data = self.load_buyer_data(file_name) # 바이어의 영문 이름 담긴 리스트 로드
        search_data = [] # 기존 데이터에 검색 결과 첨부
        for item in buyer_data['data']:
            search_result = [] # 검색 결과를 저장
            english_name = item['trgtpsnNm'].replace('?','') # 주요 검색어로 이름 축라
            
            input_ = item['trgtpsnNm']
            nation = item['korNm']

            instruction = f"1. Translate the text into the target language {nation} \n 2. Translate the word list ['contact', 'product', 'information'] based on the translated language.\n3. Your response should be in the following JSON format: ['translation': 'your translation', 'language': 'target language', 'word list': ~]"
            # """
            # {'translation': 'Sani-Prevent kereskedelmi és szolgáltató korlátolt felelősségű társaság',
            # 'language': 'Hungarian',
            # 'word_list': {'contact': 'kapcsolat',
            # 'product': 'termék',
            # 'information': 'információ'}}
            # """
            prompt = self.get_prompt(input_, instruction)
            
            # 1. 우선 검색의 정확성을 위해 해당 바이어가 소재하는 국가 기준으로 번역해서 검색을 하도록 함
            ## Gemini API를 활용해 번역함
            try:
                time.sleep(2)
                url = BuyerSearchClient.GEMINI_ENDPOINT
                params = {'key': BuyerSearchClient.GOOGLE_GEMINI_API_KEY}
                data = {
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }]
                    }
                response = BuyerSearchClient.request(url=url,
                                                    params=params,
                                                    data=data)
                text_response = text_response = response.json()['candidates'][0]['content']['parts'][0]['text'] # 번역된 text
                item['translatedText'] = text_response
                
            except Exception as e:
                print(e)
                print("[error] detected!, stopped with input", input_)

            
            # 영어로 검색하는 쿼리
            query_raw = f'{english_name} contact | {english_name} product | {english_name} information'

            # 바이어 국가의 언어를 기준으로 검색하는 쿼리
            try:
                # 결과물을 json으로 만듬
                buy_item = json.loads(item['translatedText'].split('```json')[-1].strip().rstrip('`'))
                # 번역된 정보 추출
                name_translated = buy_item['translation']
                word_list = buy_item['word_list']
                query_translated = f"{name_translated} {' | '.join([f'{name_translated} {word_translated}' for word_translated in word_list.values()])}"
            except:
                query_translated = None
            

            # 웹페이지 정보 있으면 웹페이지 정보 가져오기
            try:
                website = item['hmpgAddr'].replace('www.', '').replace('http://', '').replace('https://', '').replace('/', '')
                query_site = f'site:{website}'
            
            except:
                query_site = None

            for query in [query_raw, query_translated, query_site]:
                if query:
                    print(f"Query: {query}")
                    time.sleep(1)
                    search_result_df = self.request_google_api(query=query, wanted_row=10)
                    search_result.append(search_result_df)
            
            # 해당 칸에 검색 결과를 필터링하는 모델 추가해야함. company_description를 기반으로 회사정보와 관련이 있는지 필터링함.
            company_info = {
            'name': item.get('trgtpsnNm', ''),
            'representative': item.get('rprsnt1Nm', ''),
            'product': item.get('prod1Nm', ''),
            'website': item.get('hmpgAddr', '')
            }

            company_description = f"""
            Company Name: {company_info['name']}
            Representative: {company_info['representative']}
            Product: {company_info['product']}
            Website: {company_info['website']}
            """

            item['company_description'] = company_description
            search_result = json.loads(pd.concat(search_result).reset_index(drop=True).to_json(orient='records'))

            # search_result 필터링
            
            # 검색 결과 저장
            item['search_result'] = search_result
            search_data.append(item)
        buyer_data['data'] = search_data # 기존 데이터에서 구글 검색 결과 추가한 데이터 갱신
        return buyer_data

if __name__ == "__main__":
    pass
