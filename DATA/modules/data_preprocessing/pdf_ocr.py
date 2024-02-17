import os, pickle, cv2
import numpy as np
import pandas as pd
import layoutparser as lp
import PIL
import json
import warnings
import time
import dotenv # 환경변수 프로젝트 단위로 불러오기

from tqdm import tqdm
from glob import glob
from tqdm.auto import tqdm
from typing import *
from pymongo import MongoClient
from openai import AzureOpenAI


dotenv_file = dotenv.find_dotenv(os.path.join('config', '.env'))
dotenv.load_dotenv(dotenv_file)

class OCRPreprocessing:
    MONGODB_URL = os.environ.get("MONGODB_URL")
    SOURCE_DIR = os.path.join('raw', 'kotra', 'country_report')
    SAVE_DIR = os.path.join('output', 'country_report')
    
    # embedding용 azure openai 환경변수
    AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
    DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME")
    ADA2_EMBEDDING_API_KEY = os.environ.get("ADA2_EMBEDDING_API_KEY")
    ADA2_EMBEDDING_API_VERSION = os.environ.get("ADA2_EMBEDDING_API_VERSION")

    def __init__(self):
        if not os.path.exists(os.path.join(OCRPreprocessing.SAVE_DIR, 'txt')):
            os.makedirs(os.path.join(OCRPreprocessing.SAVE_DIR, 'txt'))
        if not os.path.exists(os.path.join(OCRPreprocessing.SAVE_DIR, 'json')):
            os.makedirs(os.path.join(OCRPreprocessing.SAVE_DIR, 'json'))
        self.model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                              extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6],
                                              label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})

    @staticmethod
    def load_pdf(file_name: str) -> Tuple[List, List]:
        """데이터 로드"""
        file_path = os.path.abspath(os.path.join(OCRPreprocessing.SOURCE_DIR, file_name)) # 상대경로 하면 오류가 생겨서 절대경로로 함
        try:
            pdf_layout, pdf_images = lp.load_pdf(file_path, load_images=True,use_text_flow=True,dpi=144)
            return (pdf_layout, pdf_images)
        except FileNotFoundError as e:
            print(e)
    
    @staticmethod
    def save_tmp_data(country: str, data: str, file_name: str, file_type="txt") -> None:
        
        """문자열을 텍스트 파일로 저장"""
        if file_type == "txt":
            file_fullname = f"ocr_{file_name}.txt"
            with open(os.path.join(OCRPreprocessing.SAVE_DIR, 'txt', file_fullname), 'w') as file:
                file.write(data)
            return
            
        if file_type == "json":
            file_fullname = f'ocr_{file_name}_{page_num}.json'
            # 페이지 나누기            
            page_list = OCRPreprocessing.page_delimiter(data)
            # print(page_list)
            # print('page:', len(page_list))
            # 개별 페이지 저장
            for page_num, page in tqdm(enumerate(page_list, start=1)):
                if len(page) > 1:  # 페이지의 내용이 있는 경우에만 JSON 파일 생성
                    with open(os.path.join(OCRPreprocessing.SAVE_DIR, 'json', file_fullname), 'w') as json_file:
                        json.dump({
                            "country": country, 
                            "file_name": file_name, 
                            "page": page_num,
                            "text_original": page,
                            "embedding": OCRPreprocessing.get_embedding(page)
                        }, json_file, ensure_ascii=False, indent=4)
                    time.sleep(1)
                # json.dump({"country": country, "file_name": file_name, "page": page_list}, json_file, ensure_ascii=False, indent=4)

            return

            
        raise Exception(f"타입 오류")
    
    def get_embedding(text: str):
        client = AzureOpenAI(
                            api_key         = OCRPreprocessing.ADA2_EMBEDDING_API_KEY,
                            api_version     = OCRPreprocessing.ADA2_EMBEDDING_API_VERSION,
                            azure_endpoint  = OCRPreprocessing.AZURE_ENDPOINT
                            )

        deployment_name = OCRPreprocessing.DEPLOYMENT_NAME

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
        client = MongoClient(OCRPreprocessing.MONGODB_URL)
        # Specify the database and collection
        
        db = client["hscode"]
        collection = db["commodity"]
        
        # 저장되어 있는 임시파일 로드
        json_data_list = []
        for root, _, files in os.walk(os.path.join(OCRPreprocessing.SAVE_DIR, 'json')):
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
    def page_delimiter(text: str, delimiter: str = None) -> List:
        """page단위별로 나누어주는 메서드"""
        if delimiter == None:
            delimiter = "\n==============================\n"
        return text.split(delimiter)\
        
    def process_page(self, pdf_layout: List, pdf_images: List) -> List[dict]:
        """각 페이지의 텍스트 레이아웃을 처리하고 페이지 구조를 반환."""
        pages = []
        for pgn, layout in enumerate(tqdm(pdf_layout)):
            page = {}
            page['words'] = pd.DataFrame()
    
            pil_image = pdf_images[pgn].convert('RGB')
            image = np.array(pil_image)
            image = image[:, :, ::-1].copy()
            detected_layouts = self.model.detect(image)
    
            for i in layout:
                page['words'] = pd.concat([page['words'], pd.DataFrame([i.to_dict()])], ignore_index=True)
    
            for count, detected_layout in enumerate(detected_layouts):
                section_id = f'layout_{count+1}'
                section = {'layout': detected_layout, 'type': detected_layout.to_dict()['type'], 'words': pd.DataFrame()}
                page[section_id] = section
    
            for word in layout:
                for key in page.keys():
                    if 'layout' in key:
                        section = page[key]
                        if word.is_in(section['layout'], center=True):
                            dic = word.to_dict()
                            dic['section_type'] = section['type']
                            section['words'] = pd.concat([section['words'], pd.DataFrame([dic])], ignore_index=True)
    
            pages.append(page)
        return pages

    def extract_pdf_content(self, pages: List[dict]) -> str:
        """페이지 구조에서 PDF 콘텐츠를 추출하고 텍스트로 변환."""
        pdf_content_text = ''
        for page in tqdm(pages):
            for key in page.keys():
                if 'layout' in key:
                    section = page[key]
                    if section['type'] == 'Text' or section['type'] == 'Title':
                        content = ' '.join(section['words']['text']) if 'text' in section['words'] else ''
                        pdf_content_text += content + '\n'
                    elif section['type'] == 'Table':
                        content = ' '.join(section['words']['text']) if 'text' in section['words'] else ''
                        pdf_content_text += content + '\n'
                    elif section['type'] == 'List':
                        content = ' '.join(section['words']['text']) if 'text' in section['words'] else ''
                        pdf_content_text += content + '\n'
                    elif section['type'] == 'Figure':
                        content = ' '.join(section['words']['text']) if 'text' in section['words'] else ''
                        pdf_content_text += content + '\n'
            
            # 페이지 내용이 유효하며, 페이지가 끝날 때마다 bar 붙임
            pdf_content_text += "\n==============================\n"
        return pdf_content_text


    def convert_to_text(self, pdf_layout: List, pdf_images: List) -> str:
        """PDF 이미지와 레이아웃을 활용하여 텍스트로 변환."""
        if len(pdf_layout) == 0 or len(pdf_images) == 0:
            raise Exception("변환할 파일이 존재하지 않습니다.")
        if len(pdf_layout) != len(pdf_images):
            raise Exception("페이지와 이미지 수가 일치하지 않습니다.")
            
        pages = self.process_page(pdf_layout, pdf_images)
        pdf_content_text = self.extract_pdf_content(pages)
        return pdf_content_text


# 예시 코드
if __name__ == "__main__":
    ocr = OCRPreprocessing()

    sample = "output/kotra/foreign_report/멕시코.pdf" # 샘플 데이터
    sample_pdf_layout, sample_pdf_images = ocr.load_pdf(sample) # 데이터 로드
    result = ocr.convert_to_text(sample_pdf_layout, sample_pdf_images) # convert
    ocr.save_data(result, "멕시코", 'txt') # save txt
    ocr.save_data(result, "멕시코", 'json') # save json
