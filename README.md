# BYBL : Beyond Your Border with LLM


<p align="center">
  <img src="https://github.com/KPMG-2024/KPMG-BYBL/assets/62554639/1f08a2e0-baf1-4cb0-ac03-f4737b9e47af" alt="BYBL Image" width="500">
</p>

<div align=center>
<h3>수출 기업을 위한 업무 자동화 솔루션: BYBL</h3>
</div>



## 📚 OverView
- 수출 기업들의 바이어 발굴, 해외시장 정보 등 각종 정보 수집의 어려움을 해결하고 업무 효율을 높이고자 제안
- 제안 서비스
  - 해외시장 및 바이어 조사 자동화
  - RAG 기반 질의응답 챗봇 서비스
  - Cold-Mail 자동 작성 서비스

<br></br>
## 📁 Structure
- `DATA` : 데이터 수집, 가공 파이프라인 코드 모음
- `MODEL` : 필터링 모델 훈련 코드 모음
- `FE` : 서비스 프론트엔드 코드 모음
- `BE` : 서비스 백엔드 코드 모음 

<br></br>

## 🛠️ Skills

<div>
<h3>Language</h3>
<img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
</div>


<div>
<h3>Web Service</h3>
<img alt="React" src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=white">
<img alt="Tailwind CSS" src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white">
<img alt="Flask" src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
<img alt="MongoDB" src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white">
<img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-00FFD1?style=for-the-badge&logo=openai&logoColor=white">
<img alt="LangChain" src="https://img.shields.io/badge/LangChain-3b5998?style=for-the-badge&logo=&logoColor=white">
<img alt="Tableau" src="https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white">
</div>

<div>
<h3>Modeling & Data Preprocessing</h3>
<img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white">
<img alt="scikit-learn" src="https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white">
<img alt="Hugging Face" src="https://img.shields.io/badge/Hugging_Face-3F51B5?style=for-the-badge&logo=huggingface&logoColor=white">
</div>

<div>
<h3>Data Collection</h3>
<img alt="Selenium" src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white">
<img alt="Beautiful Soup" src="https://img.shields.io/badge/Beautiful_Soup-4E148C?style=for-the-badge&logo=beautifulsoup&logoColor=white">
</div>

<br></br>

## 🖥️ Service

### 1. 해외시장 및 바이어 조사 자동화
- **국제통일상품분류체계**(이하 HSCODE)를 기반으로 작동
- 수출 기업이 주로 수출하는 상품의 HSCODE를 입력하면 해당 상품과 관련있는 유망시장 정보, 국가 및 상품정보, 바이어 정보를 한번에 수집, 데이터베이스화
- 고객과 관련 있는 정보만 자동으로 수집, 저장하여 대시보드 및 챗봇, Cold-Mail 작성 서비스의 기반이 됨
- 데이터 출처 : 대한무역투자진흥공사(KOTRA) 및 한국무역보험공사(K-SURE)
![image](https://github.com/KPMG-2024/KPMG-BYBL/assets/62554639/c1e69aac-d1dd-42bc-ac72-0d60b06a5cd8)


### 2. RAG 기반 질의응답 챗봇 서비스
- 데이터 수집 단계에서 수집된 각종 정보들과 생성형 AI를 기반으로 해외시장 정보, 바이어 정보 등 필요한 정보에 대해 질의응답하는 서비스
- 사전 구축한 DB 및 RAG를 바탕으로 생성형 AI를 사용하면서 발생하는 **할루시네이션(Hallucination) 현상을 최소화하며 사용자에게 필요한 정보를 제공**
- 추가로 검색 및 질의응답에서 얻은 대화 내용을 저장할 수 있는 아카이브를 제공하여 필요한 정보 다시 볼 수 있을뿐만 아니라 아카이브를 기반으로 질의응답할 수 있도록하여 편의성 높임
![image](https://github.com/KPMG-2024/KPMG-BYBL/assets/62554639/a03f409d-be49-4dba-86ab-30d310972f00)



### 3. Cold Mail 작성 서비스
- 사전 구축한 바이어 DB에 대한 정보를 바탕으로 **잠재 바이어 맞춤형 콜드 메일 초안** 생성
- 바이어의 회사 및 주력 상품 정보, 언어 등을 토대로 이메일 제목 및 본문을 생성 뿐만 아니라 전송도 할 수 있는 One-Stop 서비스
- 비즈니스 환경을 고려하여 이메일 제목 뿐만 아니라 본문을 잘 생성할 수 있도록 프롬프트 엔지니어링
![image](https://github.com/KPMG-2024/KPMG-BYBL/assets/62554639/02175096-4cb1-48d5-872b-d0810024284e)





