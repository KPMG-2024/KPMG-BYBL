import os
import json
from typing import *
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import json
from openai import AzureOpenAI
import time
import sys
from tqdm import tqdm
import requests
import tiktoken
from bs4 import BeautifulSoup
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from pymongo import MongoClient

import dotenv # 환경변수 프로젝트 단위로 불러오기
dotenv_file = dotenv.find_dotenv('../config/.env')
dotenv.load_dotenv(dotenv_file)
# import pymongo
# from pymongo import MongoClient

"""
구글 검색 api를 통해서 나온 바이어 정보 중, 관련있다고 생각하는 바이어 정보만 추출하는 과정
"""

# 1. 우선 구글에 서치된 파일들을 모두 로드

# 2. 그것들을 모두 필터에 통과시킴

# 3. 필터에 남은 파일들은 몽고 DB에 넣음!!

# 3. 몽고 DB에 들어가야 할 데이터
## 3.1 last-updated
## 3.2 hscode
## 3.3
class BuyerFilter():
    SOURCE_DIR = os.path.join('raw', 'google', 'buyer_info', 'json')
    SAVE_DIR = os.path.join('output', 'buyer', 'json')
    MONGODB_URL = os.environ.get("MONGODB_URL")
    GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")

    # 해당 사이트는 크롤링을 허용하지 않는 경우가 있으므로, 크롤링을 허용하지 않는 사이트는 제외합니다.
    EXCLUDED_LINKS = ['twitter', 'linkedin', 'facebook']

    def __init__(self) -> None:
        if not os.path.exists(BuyerFilter.SAVE_DIR):
            os.makedirs(BuyerFilter.SAVE_DIR)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForSequenceClassification.from_pretrained("hamzzi/xlm-roberta-filter-search", num_labels=3).to(self.device) # 모델 업로드
        self.tokenizer = AutoTokenizer.from_pretrained("hamzzi/xlm-roberta-filter-search") # 모델에 사용할 토크나이저


    def load_data(self) ->List[Dict]:
        """바이어 데이터 로드"""
        json_data_list = []
        for root, _, files in os.walk(BuyerFilter.SOURCE_DIR):
            # 디렉토리에 존재하는 파일 로드
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data_list.append(json.load(f))
        return json_data_list    


    def filter_data(self, data:List[Dict]):
        """사전에 구축한 필터링 모델을 거쳐 관련있는 자료인지 추출"""
        filtered_data = []
        for file in data: # json폴더 전체에서 하나의 파일을 꺼낸 다음
            for item in tqdm(file['data']): # 하나의 파일에서 하나의 회사를 고른다음
                print(item['trgtpsnNm'], '에 대한 데이터 수집을 시작합니다.')
                
                item['company_description'] = "\n".join([line.strip() for line in item['company_description'].strip().split('\n')]).strip() # 문자열 전처리
                
                # 추가적으로 담을 정보들
                email_found = False # 이메일 검색을 위한 bool
                item['email'] = None
                item['search_total_info'] = ""
                product_info = []
                useful_info = []
                
                for search_result in tqdm(item['search_result']):
                    
                    # 탐색 시간 측정
                    _t = time.perf_counter()
                    link = search_result['Link']

                    # 제외할 링크가 있는 경우 제외
                    if any(excluded_link in link for excluded_link in BuyerFilter.EXCLUDED_LINKS):
                        continue
                    
                    # 필터링 모델 입력 만들기
                    inputs = self.tokenizer(
                        item['company_description'],
                        search_result['Concated_text'],
                        truncation=True,
                        return_token_type_ids=False,
                        pad_to_max_length=True,
                        add_special_tokens=True,
                        max_length=512,
                        return_tensors="pt" 
                    )

                    input_ids = inputs['input_ids'].to(self.device)
                    attention_mask = inputs['attention_mask'].to(self.device)

                    # 모델에 입력 데이터 전달하여 결과 얻기
                    with torch.no_grad():
                        output = self.model(input_ids, attention_mask=attention_mask)

                    # 예측 결과 가져오기
                    logits = output.logits
                    probabilities = torch.nn.functional.softmax(logits, dim=1)
                    predictions = torch.argmax(probabilities, dim=1).cpu().numpy()

                    # 관련있는 정보만 남겨두기
                    if predictions[0] != 2:
                        search_result['relevant'] = False
                        continue
                    
                    search_result['relevant'] = True
                    
                    # 해당 링크에 리퀘스트 보내고 HTML 파싱하기
                    try:
                        response = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
                        Link_html = response.text

                        # BeautifulSoup을 사용하여 HTML 파싱
                        soup = BeautifulSoup(Link_html, 'html.parser')

                        # <script>, <source>, <img> 태그 제거하기 -> 해당 태그는 정보를 담고 있지않는 점에서 속도 및 비용 절감을 위해 없앰
                        for script in soup(['script', 'source', 'img']):
                            script.extract()
                        
                        Link_html = soup.prettify()

                    except requests.Timeout:
                        Link_html = False
                        print("요청 시간 초과되었습니다.")

                    except requests.RequestException as e:
                        Link_html = False
                        print("Request failed:", e)
                        
                    if Link_html is not False and Link_html != '':
                        
                        prompt = self.get_prompt(Link_html)

                        # 인풋 가격 계산
                        search_result['input_price'] = 0.01 * self.check_tokens(prompt) / 1000
                        # time.sleep(3)
                        
                        # GEMINI API 요청해서 현재 내용 summary해달라는 내용
                        try:
                            output = self.get_response(prompt=prompt)
                                                            
                            tmp_output = json.loads(output) # 문자열 -> 딕셔너리
                            # 이메일 검색
                            if email_found == False and (tmp_output['Email'] != None and tmp_output["Email"] != "None"):
                                print(f"email : {tmp_output['Email']}")
                                item['email'] = tmp_output['Email']
                                email_found = True
                            
                            
                            # 유용한 정보 등 RAG에 사용될 정보 모아두기
                            if tmp_output["Product Information"] != None and tmp_output["Product Information"].strip() != "None":
                                product_info.append(tmp_output["Product Information"])
                            if tmp_output["Useful Information"] != None and tmp_output["Useful Information"].strip() != "None":
                                useful_info.append(tmp_output["Useful Information"])
                                
                            
                            search_result['link_content_summary'] = output
                            search_result['output_price'] = 0.03 * self.check_tokens(output) / 1000
                            print("성공")
                    
                        except Exception as e:
                            print(e)
                            print("[error] 잼민이 API 요청 실패 :", link)
                        
                            # # 에러 발생하면 1분 대기 후 다시 보냄.
                            # try:
                            #     # time.sleep(60)
                            #     # time.sleep(2)

                            #     output = self.get_response(prompt=prompt)

                            #     tmp_output = json.loads(output) # 문자열 -> 딕셔너리
                            #     # 이메일 검색
                            #     if email_found == False and tmp_output['Email'] != None :
                            #         item['email'] = tmp_output['Email']
                            #         email_found = True
                                
                                
                            #     # 유용한 정보 등 RAG에 사용될 정보 모아두기
                            #     if tmp_output["Summary"] != None:
                            #         summary.append(tmp_output["Summary"])
                            #     if tmp_output["Product Information"] != None:
                            #         product_info.append(tmp_output["Product Information"])
                            #     if tmp_output["Useful Information"] != None:
                            #         useful_info.append(tmp_output["Useful Information"])
                                
                            #     search_result['link_content_summary'] = output
                            #     search_result['output_price'] = 0.03 * self.check_tokens(output) / 1000
                            #     print("성공")

                            # except Exception as e:
                            #     print(e)
                            #     print("[error] 아직도 실패 :", link)
                            #     search_result['link_content_summary'] = None
                            #     search_result['output_price'] = None
                        
                        # 시간 측정
                        t = time.perf_counter() - _t

                        search_result['collect_time'] = t

                # 검색 결과 필터링 - input price가 없는건 관련없는 정보였거나 request에 실패한 경우이므로 제외
                filtered_results = [result for result in item['search_result'] if 'input_price' in result]
                item['search_result'] = filtered_results
                print("cnt: ", len(product_info), product_info)
                # 정보 저장
                try:
                    item['search_total_info'] = f"""
                    - Buyer overview\n{item['company_description']} \n\n- Buyer's recent activities \nProduct info : {". ".join(product_info)} \nUseful info : {". ".join(useful_info)}
                    """.strip()
                except: 
                    item['search_total_info'] = f"""
                    - Buyer overview\n{item['company_description']}
                      """.strip()
                # 데이터 임시 저장
                self.save_tmp_data(item) 
                filtered_data.append(item)
            


        return filtered_data
            
    def check_tokens(self, string: str) -> str:
        """Truncates a text string based on max number of tokens."""
        encoding = tiktoken.encoding_for_model('gpt-4')
        encoded_string = encoding.encode(string)
        num_tokens = len(encoded_string)
        
        return num_tokens

    # gemini prompt 생성 함수
    def get_prompt(self, requests_result):
        prompt = f"""
        Your task is to summairize the content in HTML source code and to extract information related to a specific company by examining HTML source code. Follow the instructions.

        Instructions:
        1. First, you summarize the HTML source code and provide a brief summary of the content in no more than 5 sentences. 
        2. You must extract information if it exists on "the company's contact details, email, company information, phone number, address, product information, and information about the representative."
        3. If there is additional useful information about the company, extract that as well and describe it in no more than 5 sentences.
        4. Provide your answer in korean in JSON format and. If a particular key's value is not available, fill it in with "None":
        {{
        "Summary": "Summary",
        "Company Name": "Company Name",
        "Email": "Email",
        "Phone Number": "Phone Number",
        "Address": "Address",
        "Product Information": "Product Information",
        "Representative": "Representative Name",
        "Useful Information": "Useful Information"
        }}

        HTML:
        {requests_result}
        """
        return prompt

    # GEMINI API 요청 함수
    def get_response(self, prompt):
        # Define the API key and URL
        API_KEY = BuyerFilter.GOOGLE_GEMINI_API_KEY  # replace with your actual API key
        URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

        # Define the headers and data for the POST request
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
            }

        # Send POST request
        response = requests.post(f"{URL}?key={API_KEY}", headers=headers, json=data)
        print(response)
        text_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        return text_response
    
    # def save_data(self):
    #     """데이터를 몽고DB에 적재"""
        
    #     return
    
    # def save_tmp_data(self, item: Dict) -> None:
    #     nation_name = item['nation_name']
    #     hscode = item['hscode']
    #     company = item['trgtpsnNm']
        
    #     """몽고DB에 저장하기 전, 미리 샘플 데이터 저장히기"""
    #     with open(os.path.join(BuyerFilter.SAVE_DIR, f"{nation_name}_{hscode}_{company}.json"), 'w') as json_file:
    #         json.dump(item, json_file, ensure_ascii=False, indent=4)

    @staticmethod
    def save_tmp_data(item: Dict) -> None:
        nation_name = item['nation_name']
        hscode = item['hscode']
        company = item['trgtpsnNm']
        
        """몽고DB에 저장하기 전, 미리 샘플 데이터 저장히기"""
        with open(os.path.join(BuyerFilter.SAVE_DIR, f"{nation_name}_{hscode}_{company}.json"), 'w') as json_file:
            json.dump(item, json_file, ensure_ascii=False, indent=4)
    
    @staticmethod        
    def save_data():
        """데이터를 몽고DB에 적재"""
        # 몽고 DB 클라이언트 설정
        client = MongoClient(BuyerFilter.MONGODB_URL)
        # Specify the database and collection
        
        db = client["buyer"]
        collection = db["search_result"]
        
        # 저장되어 있는 임시파일 로드
        json_data_list = []
        for root, _, files in os.walk(BuyerFilter.SAVE_DIR):
            # 디렉토리에 존재하는 파일 로드
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data_list.append(json.load(f)) #데이터만 따로 저장

        for item in json_data_list:
            # MongoDB Atlas에 데이터 삽입
            try:
                collection.insert_one(item)
                print("Item inserted successfully into MongoDB Atlas")
            except Exception as e:
                print(f"An error occurred while inserting the item into MongoDB Atlas: {e}")

        # MongoDB 클라이언트 종료
        client.close()
    