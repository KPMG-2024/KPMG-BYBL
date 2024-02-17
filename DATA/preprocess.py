"""
수집 데이터 전처리 코드
- collect.py에서 수집한 데이터들을 전처리 및 가공 후 DB에 적재
1. OCR을 활용해 코트라 국가보고서를 txt, json화
2. 무보 및 구글에서 얻은 바이어 정보에서 필요한 정보만 필터링
3. 코트라 상품 정보에서 해당 hscode와 비슷한 데이터만 필터링함
"""
#%%
import os
from modules.data_preprocessing import OCRPreprocessing, BuyerFilter, CommodityFilter

hs_code = "160100"  # 예시 HS Code
country = "미국"


# 1. OCR preprocessing 
print("=" * 30)
print("pdf파일 OCR 시작")

target_dir = os.path.join('raw', 'kotra', 'country_report') # 특정 디렉토리만 검색
target_dir

## 특정 폴더 내에 있는 모든 파일 이름 가져옴

report_list = []
for root, _, files in os.walk(target_dir):
    # 디렉토리에 존재하는 파일 로드
    for file in files:
        if file.endswith('.pdf'):
            report_list.append(file)

ocr = OCRPreprocessing()

for report in report_list:
    # 변환
    pdf_layout, pdf_images = ocr.load_pdf(report) # 데이터 로드
    result = ocr.convert_to_text(pdf_layout, pdf_images) # convert
    print(f"{report} converted Completed")

    # 저장(pdf확장자 제거하기 위해 [:-4] 임시로 사용)
    ocr.save_tmp_data(country, result, report[:-4], 'txt') # save txt
    ocr.save_tmp_data(country, result, report[:-4], 'json') # save json
    
ocr.save_data() # mongodb 저장
print("save completed")

print("pdf파일 OCR 완료\n\n")

# 2. buyer_filtering
print("=" * 30)
print("바이어 필터링 시작")

bf = BuyerFilter()
buyer_list = bf.load_data() # 전체 폴더의 파일 다 가져옴
print(buyer_list)

result = bf.filter_data(buyer_list)
print("필터 완료")
bf.save_data() # 몽고db 저장완료

print("바이어 필터링 완료\n\n")

#%%
# 3. commodity filtering
print("=" * 30)
print("상품 데이터 필터링 시작")

comFilter = CommodityFilter()
load_data_list = comFilter.load_data()

comFilter.filter_data(hs_code)
print("save completed to local")
comFilter.save_data()
print("save completed to mongo")

print("상품 데이터 필터링 완료")

