# Directory Structure
```
data-collection
├── modules
│   ├── data_collection.py           # 추상클래스
│   ├── kotra_hscode_industry.py     # KSIC-Industry 매칭 모듈
│   ├── kotra_market.py              # 코트라 시장 정보 수집 모듈
│   ├── kotra_foreign_report.py      # 코트라 해외 보고서 수집 모듈
│   ├── kotra_commodity.py           # 코트라 상품 정보 및 트렌드 수집 모듈
│   ├── ksure_buyer_list.py          # 무보 바이어 리스트 수집 모듈
│   ├── google_buyer_search.py       # 무보 데이터 수집 모듈 공유
│   └── ...
├── config
│   ├── base_data                    # 향후 수집의 기초가 되는 root data
│   │   ├── istans_hscd.csv
│   │   └── market_data.json
│   └── ...
└── output                           # 수집 결과 모듈
    ├── kotra                        # 코트라에서 추출한 데이터
    │   ├── market                   ## market 데이터
    │   │   ├── csv
    │   │   │   ├── hscode1
    │   │   │   │   ├── hscode1_impExpMkshRateList.csv
    │   │   │   │   └── ...
    │   │   │   └── ...
    │   │   └── json
    │   │       ├── hscode1
    │   │       │   ├── hscode_bulk.json
    │   │       │   ├── hscode1_impExpMkshRateList.json
    │   │       │   └── ...
    │   │       └── ...
    │   ├── foreign_report         ## 해외시장 보고서 데이터
    │   │   ├── pdf
    │   │   │   ├── 인도네시아
    │   │   │   │   ├── 인도네시아의발전.pdf
    │   │   │   │   └── ...
    │   │   └── commodity          ## 해외시장 상품 데이터
    │   │       └── txt
    ├── ksure                      #무보 바이어 리스트 데이터 모음
    │   ├── buyer_list
    │   │   ├── json
    │   │   │   ├── hscode1
    │   │   │   │   ├── hscode1_인도네시아_바이어이름.json
    │   │   │   │   └── ...
    │   │   │   └── ...
    │   │   └── ...
    │   └── ...
    └── google                    # 구글 바이어 정보 검색결과 데이터
        └── txt
            ├── buyer이름
            │   ├── buyer1.txt
            │   └── ...
            └── ...

```
---
