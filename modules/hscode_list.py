import json
from tqdm import tqdm
import requests
import pandas as pd
import os


def main():
    SAVE_DIR = os.path.join('kotra', 'data')

    def __init__(self, SAVE_DIR):
        if not os.path.exists(SAVE_DIR): # 폴더가 따로 없을 시, 만들어 줌
            os.makedirs(os.path.join(SAVE_DIR, 'json'))
            os.makedirs(os.path.join(SAVE_DIR, 'csv'))

    # hscd
    level1 = json.loads(requests.get('https://www.kotra.or.kr/bigdata/common/getHscdList?cdLevelCd=2&selectedHscd=&searchHscd=&searchWord=').text)['hscdList']

    for item in tqdm(level1):
        hscode_1 = item['hscd']
        item['level2'] = json.loads(requests.get(f'https://www.kotra.or.kr/bigdata/common/getHscdList?cdLevelCd=4&selectedHscd={hscode_1}&searchHscd=&searchWord=').text)['hscdList']

        for item2 in item['level2']:
            hscode_2 = item2['hscd']
            item2['level3'] = json.loads(requests.get(f'https://www.kotra.or.kr/bigdata/common/getHscdList?cdLevelCd=6&selectedHscd={hscode_2}&searchHscd=&searchWord=').text)['hscdList']

    with open(os.path.join(SAVE_DIR, 'json', 'kotra_hscode_list.json')) as f:
        json.dump(level1, f, ensure_ascii=False, indent=2)


    # Extract level1, level2, and level3 data into a list
    all_data = []
    for item in level1:
        level1_info = {
            'hscd_level1': item['hscd'],
            'cmdltName_level1': item['cmdltName'],
            'cmdltEngName_level1': item['cmdltEngName'],
        }
        
        for level2_item in item['level2']:
            level2_info = {
                'hscd_level2': level2_item['hscd'],
                'cmdltName_level2': level2_item['cmdltName'],
                'cmdltEngName_level2': level2_item['cmdltEngName'],
            }
            
            for level3_item in level2_item['level3']:
                level3_info = {
                    'hscd_level3': level3_item['hscd'],
                    'cmdltName_level3': level3_item['cmdltName'],
                    'cmdltEngName_level3': level3_item['cmdltEngName'],
                }
                
                # Combine level1, level2, and level3 information
                combined_info = {**level1_info, **level2_info, **level3_info}
                all_data.append(combined_info)

    # Create a DataFrame from all_data
    df = pd.DataFrame(all_data)

    df.to_csv(os.path.join(SAVE_DIR, 'json', f'kotra_hscode_list.csv'), index=False, encoding='utf-8')

if __name__ == "__main__":
    main()