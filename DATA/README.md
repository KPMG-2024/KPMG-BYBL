## 설명
- 서비스에서 사용되는 다양한 데이터들을 수집, 전처리하여 DBMS에 최종적으로 저장하도록 설계하였다.
- 데이터 원천
  - KOTRA 트라이빅, 해외시장 뉴스, 국가,지역정보
  - 한국무역보험공사 바이어 데이터
  - 구글 검색을 통한 바이어 데이터(Search API를 활용)

- 데이터 수집 구조
  - `modules/data_collection`의 커스텀 모듈을 활용해 바이어, 보고서, 각종 통계정보 데이터 수집하여 `raw` 폴더에 저장
  - 수집된 데이터는 `modules/data_preprocessing`을 통해 OCR을 통한 텍스트 추출, fine-tuning한 필터링 모델을 활용해 전처리
  - 전처리한 최종 데이터는`output`폴더에 저장함과 동시에 MongoDB에 저장함

---
## Structure
```shell
├── collect.py                 # 데이터 수집 실행파일
├── preprocess.py              # 데이터 전처리 실행파일
├── config                     # 환경설정, 수집에 필요한 base data 저장 공간
│   └── base_data
│       ├── istans_hscd.json
│       ├── istans_hscd_info.csv
│       ├── ksure_nation_code_list.json
│       └── nation_code_list.json
│
├── modules                    # 데이터 수집, 전처리에 필요한 커스텀 모듈
│   ├── data_collection        # 데이터 수집 모듈
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── data_collection.py
│   │   ├── google_buyer_search.py
│   │   ├── kotra_hscode_industry.py
│   │   ├── kotra_market.py
│   │   ├── kotra_news_trend.py
│   │   └── ksure_buyer_list.py
│   └── data_preprocessing      # 데이터 전처리 모듈
│       ├── __init__.py
│       ├── buyer_filter.py
│       ├── commodity_filter.py
│       └── pdf_ocr.py
│
├── raw                         # 데이터 수집 끝난 원천(raw) 데이터
│   ├── google
│   │   └── buyer_info
│   ├── kotra
│   │   ├── country_report
│   │   ├── market
│   │   └── news
│   └── ksure
│       └── buyer_list      
│
└── output                      # 원천 데이터를 전처리, 가공한 최종 데이터
    ├── buyer
    │   └── json
    ├── commodity
    │   └── json
    └── country_report
        ├── json
        └── txt
```

---
