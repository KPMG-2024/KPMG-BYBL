from modules.data_collection import HSCodeIndustryClient, KotraMarketDataClient, KotraNewsClient, KsureBuyerClient

"""
0. 사전 데이터 수집
"""

# 0.0 Base Data인 KSIC-HSCode matching 데이터 생성
try:
    hscodeGen = HSCodeIndustryClient()
    # 산업분류코드 데이터 가져오기
    ksic_df = hscodeGen.load_ksic()
    print("Success to load ksic")

    # 매칭 데이터 생성
    matching_data = hscodeGen.generate_matching_data(ksic_df)
    print("Complete generating matching data")
    
    # 데이터 저장
    hscodeGen.save_data(matching_data, file_type='json')
    print("Complete saving json")
    hscodeGen.save_data(matching_data, file_type='csv')
    print("Complete saving csv")

# 이미 매칭 파일이 존재할 경우 
except Exception as e:
    print(e)
    print("이미 파일이 존재합니다.")


"""
1. KOTRA, 한국무역보험공사(ksure)에서 데이터 수집
- hscode, 국가명 기준으로 데이터를 수집한다
"""

hs_code = "160100"  # 예시 HS Code
country = "미국"

# 1.1 코트라 트라이빅 - hscode별 품목별 유망
print("=" * 30)
print("코트라 무역정보 수집 시작")
client = KotraMarketDataClient()

client.collect_market_data(hs_code) # 코드라에 API요청해서 데이터 가져오기
print("Success to collect data")

client.save_bulk_data() # 전체 벌크 데이터 json으로 저장
print("Complete saving bulk data")

client.save_all_data(file_type='json') # 각 도메인별로 파일 각각 json으로 저장
client.save_all_data(file_type='csv') # 각 도메인별로 파일 각각 csv파일로 저장
print("Complete saving")
print("코트라 무역정보 수집 완료\n\n")

# 1.2 코트라 해외시장뉴스 - 상품 산업에서 데이터 수집
print("=" * 30)
print("코트라 상품 데이터 수집 시작")
news_client = KotraNewsClient()

# 데이터가 없을 시 예외처리
try:
    news_data = news_client.collect_news_data(country, data_per_page=80) # 상품 관련 뉴스 데이터 추출
    print("Success to collect data")
    news_client.save_data(news_data) # 불러온 데이터 저장
    print(f"Complete saving {country} data")

except Exception as e:
    print("An error occurred:", e)

print("코트라 상품 데이터 수집 완료\n\n")

## 1.3 무보 바이어 데이터 추출
print("=" * 30)
print("무보 바이어 데이터 수집 시작")
buyer_client = KsureBuyerClient()

buyer_list = None

# 산업 코드 가져오기
industry_code = buyer_client.get_industry_code(country, hs_code)
print("산업코드 가져오기")

# 무보에서 데이터 가져오기
try:
    buyer_list = buyer_client.collect_buyer(country, industry_code, hs_code)
except Exception as e:
    print(e)
    buyer_client.quit_selenium_driver()

# 데이터 저장(결과가 하나라도 있을 경우)
if buyer_list is not None:
    buyer_client.save_data(buyer_list, file_type='json') # json파일 저장하
    buyer_client.save_data(buyer_list, file_type='csv') # csv파일 저장
    print("저장 성공")

print("무보 바이어 데이터 수집 완료\n\n")


"""
2. 바이어 세부정보 구글 search API를 활용한 데이터 수집
- 바이어 데이터를 토대로 구글에서 바이어에 대한 자세한 정보 얻기 위함
- 사전 데이터 : 무보에서 얻은 바이어 데이터가 수집되어야 함
"""

# 2.1 바이어 구글 검색
print("=" * 30)- 
print("구글 검색 시작")
from modules.data_collection import BuyerSearchClient

searchClient = BuyerSearchClient()
buyer_list = searchClient.collect_buyer_search_info(file_name=f"{country}_{hs_code}.json")

print('load completed')
searchClient.save_data(buyer_list)
print('save completed')
print("구글 검색 바이어 데이터 수집 완료\n\n")
