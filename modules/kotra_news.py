import requests
import json
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

# POST 요청을 보낼 URL
url = "https://dream.kotra.or.kr/ajaxf/frNews/getKotraBoardList.do"

# POST 데이터 설정
data = {
    'pageNo': 1,
    'pagePerCnt': 10,
    'SITE_NO': 3,
    'MENU_ID': 170,
    'CONTENTS_NO': 1,
    #bbs 관련 파라미터는 꼭 넣어야함.
    'bbsGbn': '01',
    'bbsSn': '243,254,254,403,257',
    'pNttSn': '',
    #레코드는 굉장히 많이 요청할 수 있음
    'recordCountPerPage': 10,
    'viewType': '',
    'pNewsGbn': '',
    'pStartDt': '',
    'pEndDt': '',
    #검색어
    'sSearchVal': '',
    #리전
    'pRegnCd': '',
    #국가
    'pNatCd': '',
    #무역관
    'pKbcCd': '',
    #산업
    'pIndustCd': '',
    #hscode
    'pHsCode': '',
    'pHsCodeNm': '',
    'pHsCdType': ''
}

# POST 요청 보내기
response = requests.post(url, data=data)

# JSON 파싱
kotra_commodity_info = json.loads(response.text)['data']['list']

for item in tqdm(kotra_commodity_info):
    ntt_sn = item['NTT_SN']
    bbs_sn = item['BBS_SN']

    url = f'https://dream.kotra.or.kr/kotranews/cms/news/actionKotraBoardDownDetail.do?MENU_ID=170&pNttSn={ntt_sn}&bbsSn={bbs_sn}'

    html_content = requests.get(url).text

    # BeautifulSoup로 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 모든 테이블을 찾아서 Markdown 형태로 변환하고 원래 위치에 삽입
    for table in soup.find_all('table'):
        # Pandas를 사용하여 HTML 테이블을 읽고 Markdown으로 변환
        markdown = pd.read_html(str(table), encoding='utf-8', header=0)[0].to_markdown(index=False)
        
        # Markdown 텍스트를 포함하는 새로운 <p> 태그 생성
        new_tag = soup.new_tag("p")
        new_tag.string = markdown
        
        # 원본 테이블을 새로운 <p> 태그로 교체
        table.replace_with(new_tag)

    lst= []
    # 모든 <p> 요소를 찾아 텍스트를 합치기
    combined_text = ''
    for element in soup.find_all():
        if element.name == 'p' and element.name != 'table':
            combined_text += element.get_text() + '\n'
        elif element.name == 'table':
            # 테이블이 발견되면 Pandas를 사용하여 테이블을 읽고 텍스트로 변환하여 추가
            table_text = pd.read_html(str(element), encoding='utf-8', header=0)[0].to_markdown(index=False)
            combined_text += table_text + '\n'
    
    item['content'] = combined_text
    

