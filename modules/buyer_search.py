from datetime import datetime
import os
import sys
import urllib.request
import pandas as pd 
import json
import re 
import requests
import time

Google_SEARCH_ENGINE_ID = ''
Google_API_KEY = ''
Google_gemini_API = ''

buyer_data_path = '/home/disl/mnt/mydisk/Train/buyer_translated.json'

Trash_Link = ["youtube"]

def Google_API(query, wanted_row):
    query= query.replace("|","OR")
    #query += "-filetype:pdf"
    start_pages=[]

    df_google= pd.DataFrame(columns=['Title','Link','Description','Concated_text'])

    row_count =0 

    for i in range(1,wanted_row+1000,10):
        start_pages.append(i)

    for start_page in start_pages:
        # &cr=countryUS &lr=lang_en 넣으면 국가, 언어 설정 가능
        url = f"https://www.googleapis.com/customsearch/v1?key={Google_API_KEY}&cx={Google_SEARCH_ENGINE_ID}&q={query}&start={start_page}"
        data = requests.get(url).json()
        search_items = data.get("items")
        
        try:
            for i, search_item in enumerate(search_items, start=1):
                # extract the page url
                link = search_item.get("link")
                if any(trash in link for trash in Trash_Link):
                    pass
                else: 
                    # get the page title
                    title = search_item.get("title")
                    # page snippet
                    descripiton = search_item.get("snippet")
                    
                    concated_text = f"Title:{title}\nLink:{link}\nDescription:{descripiton}"

                    # print the results
                    df_google.loc[start_page + i] = [title,link,descripiton,concated_text] 
                    row_count+=1
                    if (row_count >= wanted_row):
                        return df_google
                    
        except Exception as e:
            print('Error :', e)
            return df_google

    
    return df_google

def get_response(prompt):
    # Define the API key and URL
    API_KEY = Google_gemini_API  # replace with your actual API key
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

def get_prompt(input, instruction):
    prompt = f"""Instruction: {instruction}
    text: "{input}"
    JSON Output:"""

    return prompt

with open(buyer_data_path, 'r') as f:
    buyer_data = json.load(f)

for item in buyer_data:
    search_result = []

    english_name = item['trgtpsnNm'].replace('?','')
    
    # # 해당 란에는 번역을 해주는 프롬프트 및 인퍼런스가 있으나, 학습 데이터 수집 때는 미리 번역된 데이터를 사용함.
    # 해당 내용을 파파고 API로 번역하는 것도 가능한데, 시간 남으면 파파고로 하기 

    # input_ = item['trgtpsnNm']
    # nation = item['korNm']

    # instruction = f"1. Translate the text into the target language {nation} \n 2. Translate the word list ['contact', 'product', 'information'] based on the translated language.\n3. Your response should be in the following JSON format: ['translation': 'your translation', 'language': 'target language', 'word list': ~]"
    """
    {'translation': 'Sani-Prevent kereskedelmi és szolgáltató korlátolt felelősségű társaság',
    'language': 'Hungarian',
    'word_list': {'contact': 'kapcsolat',
    'product': 'termék',
    'information': 'információ'}}
    """
    # prompt = get_prompt(input_, instruction)

    # try:
    #     time.sleep(2)

    #     response = get_response(prompt)

    #     item['translatedText'] = response
        
    # except Exception as e:
    #     print(e)
    #     print("[error] detected!, stopped with input", input_)

    
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
            df = Google_API(query, 10)
            search_result.append(df)
    
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

    with open(os.path.join(os.getcwd(), 'buyer_search_result.json'), 'w') as f:
        json.dump(buyer_data, f, indent=2, ensure_ascii=False)