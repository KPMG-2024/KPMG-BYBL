#%%
import os
import json
import torch
import pandas as pd
import time
import dotenv # 환경변수 프로젝트 단위로 불러오기
from datetime import datetime
from pytz import timezone
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import *
from pymongo import MongoClient
from openai import AzureOpenAI
from tqdm.auto import tqdm

dotenv_file = dotenv.find_dotenv('../config/.env')
dotenv.load_dotenv(dotenv_file)

## 3.3
class CommodityFilter():
    """
    코트라 상품관련 뉴스, pdf보고서를 추출하기 위한 코드
    """
    
    SOURCE_DIR = os.path.join('raw', 'kotra', 'news', 'json')
    SAVE_DIR = os.path.join('output', 'commodity', 'json')
    GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
    # embedding용 azure openai 환경변수
    AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
    DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME")
    ADA2_EMBEDDING_API_KEY = os.environ.get("ADA2_EMBEDDING_API_KEY")
    ADA2_EMBEDDING_API_VERSION = os.environ.get("ADA2_EMBEDDING_API_VERSION")
    MONGODB_URL = os.environ.get("MONGODB_URL")

    def __init__(self) -> None:
        if not os.path.exists(CommodityFilter.SAVE_DIR):
            os.makedirs(CommodityFilter.SAVE_DIR)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForSequenceClassification.from_pretrained("hamzzi/xlm-roberta-filter-news", num_labels=2).to(self.device) # 관련유무 판단할 모델
        self.tokenizer = AutoTokenizer.from_pretrained("hamzzi/xlm-roberta-filter-news")

    def load_hscode_info(self, hscode:str) -> str:
        """HScode 6자리에 관한 정보 파악하기 위한 코드"""
        directory = os.path.join("config", "base_data", "istans_hscd_info.csv")
        df = pd.read_csv(directory, dtype='str')
        description = df[df['hscode'] == hscode]['description']
        return f"hscode:{hscode}\n{description}"
        
    def load_data(self) ->List[Dict]:
        """코트라 상품 DB, 뉴스데이터 로드"""
        json_data_list = []
        for root, _, files in os.walk(CommodityFilter.SOURCE_DIR):
            # 디렉토리에 존재하는 파일 로드
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data_list.append(json.load(f)['data']) #데이터만 따로 저장
        return json_data_list    


    def filter_data(self, hscode: str):
        """사전에 구축한 필터링 모델을 거쳐 관련있는 자료인지 추출"""
        
        files = self.load_data()
        hscode_info = self.load_hscode_info(hscode)
        for file in files:
            final_data = [] # 파일 단위별로 저장하기
            for item in file:
                content = item['content']
                inputs = self.tokenizer(
                            hscode_info,
                            content,
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
                
                # prediction이 1인 것(관련 있는 것)만 가져오기
                if predictions[0] == 1:
                    item['related_info'] = str(predictions[0]) # json 직렬화할때 오류 방지
                    final_data.append(item)
                    
                    
            self.save_tmp_data(final_data, hscode)
        
    @staticmethod
    def get_embedding(text: str):
        client = AzureOpenAI(
                            api_key         = CommodityFilter.ADA2_EMBEDDING_API_KEY,
                            api_version     = CommodityFilter.ADA2_EMBEDDING_API_VERSION,
                            azure_endpoint  = CommodityFilter.AZURE_ENDPOINT
                            )

        deployment_name = CommodityFilter.DEPLOYMENT_NAME

        # Send a completion call to generate an answer
        response = client.embeddings.create(
            input=text,
            model=deployment_name,
        )
        return json.loads(response.model_dump_json(indent=2))['data'][0]['embedding']
    
    @staticmethod        
    def save_data():
        """데이터를 몽고DB에 적재"""
        # 몽고 DB 클라이언트 설정
        client = MongoClient(CommodityFilter.MONGODB_URL)
        # Specify the database and collection
        
        db = client["hscode"]
        collection = db["commodity"]
        
        # 저장되어 있는 임시파일 로드
        json_data_list = []
        for root, _, files in os.walk(CommodityFilter.SAVE_DIR):
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


    @staticmethod
    def get_current_time() -> str:
        """한국 시간을 가져오는 메서드"""
        return datetime.now(timezone('Asia/Seoul')).isoformat()
    
    @staticmethod
    def save_tmp_data(data: List[Dict], hscode: str) -> None:
        """몽고DB에 저장하기 전, 미리 샘플 데이터 저장히기"""
        if len(data) < 1:
            print("해당 파일에는 일치하는 데이터가 없어 저장하지 않습니다.")
            return
        nation_name = data[0]['NAT']
        last_updated = CommodityFilter.get_current_time()
        
        for num, datum in tqdm(enumerate(data, start=1)):
            if len(datum) > 1:  # 페이지의 내용이 있는 경우에만 JSON 파일 생성
                with open(os.path.join(CommodityFilter.SAVE_DIR, f'{nation_name}_{num}.json'), 'w') as json_file:
                    json.dump({
                            "country": nation_name,
                            "hscode": hscode,
                            "last_updated": last_updated,
                            "data" : datum,
                            "text" : datum['content'],
                            "embedding": CommodityFilter.get_embedding(datum['content'])
                            }, json_file, ensure_ascii=False, indent=4)
                time.sleep(1)

    

if __name__ == "__main__" :
    comFilter = CommodityFilter()
    hscode = '650691'
    load_data_list = comFilter.load_data()
    comFilter.filter_data(hscode)
    print("저장 완료")

# %%
