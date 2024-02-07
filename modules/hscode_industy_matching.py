from tqdm import tqdm
from bs4 import BeautifulSoup
import json
import os
import requests
import pandas as pd
import time

def collect_hscode(hscode):
    hscode_info = json.loads(requests.get(f'https://www.kotra.or.kr/bigdata/bhrcMarket/hsName?hsCode={str(hscode)}').text)

    return hscode_info

def main():
    SAVE_DIR = os.path.join('etc', 'data')

    if not os.path.exists(SAVE_DIR): # 폴더가 따로 없을 시, 만들어 줌
        os.makedirs(os.path.join(SAVE_DIR, 'json'))
        os.makedirs(os.path.join(SAVE_DIR, 'csv'))

    ranges = {
        "A": [(1, 3)],
        "B": [(5, 8)],
        "C": [(10, 34)],
        "D": [(35, 35)],
        "E": [(36, 39)],
        "F": [(41, 42)],
        "G": [(45, 47)],
        "H": [(49, 52)],
        "I": [(55, 56)],
        "J": [(58, 63)],
        "K": [(64, 66)],
        "L": [(68, 68)],
        "M": [(70, 73)],
        "N": [(74, 76)],
        "O": [(84, 84)],
        "P": [(85, 85)],
        "Q": [(86, 87)],
        "R": [(90, 91)],
        "S": [(94, 96)],
        "T": [(97, 98)],
        "U": [(99, 99)],
    }

    # 숫자 범위를 알파벳으로 매핑하는 함수
    def create_mapping(ranges):
        mapping = {}
        for letter, range_list in ranges.items():
            for start, end in range_list:
                for i in range(start, end + 1):
                    # 숫자를 2글자 문자열로 변환 (예: 1 -> '01')
                    mapping[f"{i:02}"] = letter
        return mapping


    # 산업 분류 추가

    mapping_dict = create_mapping(ranges)

    url = 'https://github.com/FinanceData/KSIC/raw/master/KSIC_10.csv.gz'

    df_ksic = pd.read_csv(url, dtype='str')

    df_ksic['Industy_code'] = df_ksic['Industy_code'].str.pad(width=5, side='right', fillchar='0')

    df_ksic['대분류_코드'] = df_ksic['Industy_code'].str[:2]

    df_ksic['산업_대분류'] = df_ksic['대분류_코드'].map(mapping_dict)

    df_ksic['Industy_name'] = df_ksic['Industy_name'].replace(' ','',regex = True)

    all_results = []

    for idx in tqdm(range(len(df_ksic))):
        industy_code = df_ksic.loc[idx, 'Industy_code']

        industy_level1 = df_ksic.loc[idx, '산업_대분류']

        industy_code_string = str(industy_level1) + "$" + str(industy_code[:2]) + "$" + str(industy_code[:3]) + "$" + str(industy_code[:4]) + "$" + str(industy_code[:5]) 

        url = 'https://www.istans.or.kr/tree/IndustryRelationCode.jsp?s_dimid=ISTANS&d_dimid=HS96&s_value=' + industy_code_string

        html_content = requests.get(url)
        soup = BeautifulSoup(html_content.text, "html.parser")

        try:
            result = {}

            result['industy_code'] = industy_code

            related_hs_codes = []

            # OECD 무역코드 추출
            dd_content = soup.find_all('dd')[1].decode_contents()  # <dd> 태그 내용을 HTML 문자열로 추출
            code_descriptions = dd_content.split('<br/>') if '<br/>' in dd_content else dd_content.split('<br>')  # <br> 태그로 분리

            # 각 항목을 처리
            for item in code_descriptions:
                # 공백과 특수문자 제거
                cleaned_item = item.strip().replace('\xa0', ' ').replace('&amp;', '&')
                
                # 코드와 설명 분리
                # 마지막 괄호 ")" 위치를 찾아서 코드와 설명을 분리
                code_start_idx = cleaned_item.rfind('(') + 1
                code_end_idx = cleaned_item.rfind(')')
                
                if code_start_idx > 0 and code_end_idx > 0:
                    code = cleaned_item[code_start_idx:code_end_idx]
                    description = cleaned_item[:code_start_idx-2]  # 괄호와 코드 번호 앞까지가 설명
                    
                    # 결과 리스트에 추가
                    related_hs_codes.append({"code": code, "description": description.strip()})

            result['related_hs_codes'] = related_hs_codes

            all_results.append(result)
            
        except:
            pass
            #print(f'{industy_code}가 존재하지않습니다.')
    with open(os.path.join(SAVE_DIR, 'json', 'istans_hscd.json'), 'w') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    results = []

    for item in all_results:
        for hscode in item['related_hs_codes']:
            result = {
                'industy_code': item['industy_code'],
                'hscode': hscode['code'],
                'description': hscode['description']
            }
            results.append(result)

    hs_istans = pd.DataFrame(results).drop_duplicates(subset=['industy_code','hscode']).reset_index(drop=True)

    for idx in tqdm(range(len(hs_istans))):
         
        hscode_info = collect_hscode(hs_istans.loc[idx,'hscode'])

        hsName = hscode_info['hsName']

        parentHsName = hscode_info['parentHsName']

        hs_istans.loc[idx,'hsName'] = hsName

        hs_istans.loc[idx,'parentHsName'] = parentHsName
  
    hs_istans.to_csv(os.path.join(SAVE_DIR, 'csv', 'istans_hscd.csv'), index=False, encoding='utf-8')

if __name__ == '__main__':
    main()