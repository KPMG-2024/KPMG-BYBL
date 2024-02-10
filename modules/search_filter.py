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
import pymongo
from pymongo import MongoClient

# 몽고 DB 클라이언트 설정
client = MongoClient("your_mongodb_uri")

# Specify the database and collection
db = client["buyer"]
collection = db["search_result"]

# GEMINI API KEY
GOOGLE_API_KEY = "your key"

#토큰 수 세는 함수 
def check_tokens(string: str) -> str:
    """Truncates a text string based on max number of tokens."""
    encoding = tiktoken.encoding_for_model('gpt-4')
    encoded_string = encoding.encode(string)
    num_tokens = len(encoded_string)
    
    return num_tokens

# gemini prompt 생성 함수
def get_prompt(requests_result):
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
def get_response(prompt):
    # Define the API key and URL
    API_KEY = GOOGLE_API_KEY  # replace with your actual API key
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

    text_response = response.json()['candidates'][0]['content']['parts'][0]['text']

    return text_response

# 필터링 모델 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = AutoModelForSequenceClassification.from_pretrained("hamzzi/xlm-roberta-filter-search", num_labels=3)

model.to(device)
tokenizer = AutoTokenizer.from_pretrained("hamzzi/xlm-roberta-filter-search")

# 바이어 검색 결과 데이터 로드
with open('/Users/taewonyun/Documents/GitHub/Prototype/data_preprocessing/example2.json', 'r', encoding='utf-8') as f:
    buyer_search_result = json.load(f)

# 바이어 검색 결과 백업할 json 파일 생성
writer = open('/Users/taewonyun/Documents/GitHub/Prototype/data_preprocessing/test123.json', 'w', encoding='utf-8')

# 해당 사이트는 크롤링을 허용하지 않는 경우가 있으므로, 크롤링을 허용하지 않는 사이트는 제외합니다.
excluded_links = ['twitter', 'linkedin', 'facebook']

for item in tqdm(buyer_search_result[:1]):
    
    print(item['trgtpsnNm'], '에 대한 데이터 수집을 시작합니다.')

    for search_result in tqdm(item['search_result']):
        # 탐색 시간 측정
        _t = time.perf_counter()
        link = search_result['Link']

        # 제외할 링크가 있는 경우 제외
        if any(excluded_link in link for excluded_link in excluded_links):
            continue
        
        # 필터링 모델 입력 만들기
        inputs = tokenizer(
            item['company_description'],
            search_result['Concated_text'],
            truncation=True,
            return_token_type_ids=False,
            pad_to_max_length=True,
            add_special_tokens=True,
            max_length=512,
            return_tensors="pt" 
        )

        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)

        # 모델에 입력 데이터 전달하여 결과 얻기
        with torch.no_grad():
            output = model(input_ids, attention_mask=attention_mask)

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
            
            prompt = get_prompt(Link_html)

            # 인풋 가격 계산
            search_result['input_price'] = 0.01 * check_tokens(prompt) / 1000
            
            
            time.sleep(3)
            # GEMINI API 요청  
            try:
                output = get_response(prompt=prompt)

                search_result['link_content_summary'] = output
            
                search_result['output_price'] = 0.03 * check_tokens(output) / 1000
        
            except Exception as e:
                print(e)
                print("[error] 에러가 발견되었습니다. 다시 시도합니다. :", link)
            
                # 에러 발생하면 1분 대기 후 다시 보냄.
                try:
                    time.sleep(60)

                    output = get_response(prompt=prompt)

                    search_result['link_content_summary'] = output
            
                    search_result['output_price'] = 0.03 * check_tokens(output) / 1000

                except Exception as e:
                    print(e)
                    print("[error] 에러가 발견되었습니다. 다시 시도합니다. :", link)

                    search_result['link_content_summary'] = None
            
                    search_result['output_price'] = None
            
            # 시간 측정
            t = time.perf_counter() - _t

            search_result['collect_time'] = t

    # 검색 결과 필터링 - input price가 없는건 관련없는 정보였거나 request에 실패한 경우이므로 제외
    filtered_results = [result for result in item['search_result'] if 'input_price' in result]

    item['search_result'] = filtered_results


    # 백업을 위해 json 파일에 데이터 삽입
    json.dump(item, writer,ensure_ascii = False)
    writer.write('\n')
    writer.flush()

    # MongoDB Atlas에 데이터 삽입
    try:
        collection.insert_one(item)
        print("Item inserted successfully into MongoDB Atlas")
    except Exception as e:
        print(f"An error occurred while inserting the item into MongoDB Atlas: {e}")

# MongoDB 클라이언트 종료
client.close()
