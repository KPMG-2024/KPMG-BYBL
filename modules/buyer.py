from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
options = webdriver.ChromeOptions()

# 헤드레스 옵션은 셀레니움 킬 때 크롬을 안 키고 돌려서 로딩이 빠름. 처음 확인때만 크롬으로 돌아가는지 확인.
# options.add_argument('--headless')
options.add_argument('--no-sandbox') # 보안 기능 비활성화 (샌드박스라는 공간을 비활성화 시킨다는 뜻)
options.add_argument('--disable-dev-shm-usage') # /dev/shm(공유메모리) 디렉토리를 사용하지 않는다는 뜻
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")

# Set up the Chrome Driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

# URL to be scraped
url = 'https://www.ksure.or.kr:8443/research/buyer/buyerView.do'

# Open the web page
driver.get(url)

# 국가 검색하는 곳에 국가 검색
nationNm_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#nationNm"))
)

# 국가 이름 설정
nation_name = '일본'

# 산업 코드 설정
industry_code = '01121'

nationNm_element.send_keys(nation_name)

# 바이어명에 " "를 입력하면 왠만한 전체 바이어가 검색됨.
# 무보 플랫폼은 국가명 + 바이어명 or 국가명 + 산업명을 검색해야하는데 아마 실제 구현 시에는 국가명 + 산업명을 검색할 확률이 매우 높음.
button = driver.find_element(By.CLASS_NAME, 'btn_type')

# Click the element
button.click()

# 산업 대분류로 매칭해서 엘레먼트를 찾아줘야함. 대분류 코드를 가져오는 과정임.
soup = BeautifulSoup(driver.find_element(By.CSS_SELECTOR, '#oneStep').get_attribute('innerHTML'), 'html.parser')

a_elements = soup.find_all('a')

raw_data = {}

for a in a_elements:

    code = a['onclick'].split('"')[1]
    name = a['onclick'].split('"')[3]
    index_ = a['onclick'].split('"')[5]
    raw_data[code] = {"name": name, "index": index_}

# 가져온 코드들로 적절히 매칭해서 클릭함.
industry_key = str(industry_code[:2])

level1 = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f"//a[@onclick='clickFun2(\"{industry_key}\",\"{raw_data[industry_key]['name']}\",\"{raw_data[industry_key]['index']}\")']"))
)

# 엘리먼트를 클릭하거나 다른 작업 수행
level1.click()

level2 = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, f'a2Tag{str(industry_code[2])}'))
)

level2.click()

level3 = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, f'a3Tag{str(industry_code[3])}'))
)

# Click the element
level3.click()

level4 = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#fourStep > a'))
)

level4.click()

# 아무 엘레먼트나 클릭해서 엔터키를 누르면 검색이 됨.
nationNm_element.send_keys(Keys.ENTER)

try:
    # 첫 번째 바이어가 나타날 때까지 기다림. 만약 3초 안에 처리하면 바이어가 보통 0명인 경우라 잘 처리해주면 됨.
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#buyerTbody > tr:nth-child(1) > td.t_l'))
    )

except TimeoutException:
    # 예외가 발생하면 로딩이 오래 걸린다는 의미이므로 넉넉하게 시간을 다시 줌.
    print('로딩 중')
    element = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#buyerTbody > tr:nth-child(1) > td.t_l'))
    )

# <em> 태그 안에 있는 내용은 총 n건의 검색 결과에서 n을 가져옴.
em_element = driver.find_element(By.CSS_SELECTOR, "span.board_total em")

result_text = em_element.text

element = driver.find_element(By.CSS_SELECTOR, "#pagingId > a.btn_prev")

element.click()

# 총 클릭 페이지 계산
total_page = round(int(result_text) / 10)

for i in tqdm(range(total_page)):
    
    #다음 버튼 누르면서 계속 정보를 받아옴
    element = driver.find_element(By.CSS_SELECTOR, f"#pagingId > a.btn_next")

    element.click()

    # 2초간 기다림
    time.sleep(2)

    # 100개마다 백업해줌.
    if i % 100 == 0:
        # Filter and print the specific request
        request_list= []

        for request in driver.requests:
            if request.response and request.url == 'https://www.ksure.or.kr:8443/research/buyer/selectBuyerList.do':
                # Print the response

                json_response = request.response.body.decode('utf-8')
                new_data = json.loads(json_response)

                # Check for duplicates before adding to the list
                if new_data not in request_list:
                    request_list.append(new_data)

        with open(f'Buyer_list_{nation_name}_backup.json', 'w') as f:
            json.dump(request_list, f, ensure_ascii=False, indent=1)
                    

# post된 정보를 다 가져옴
request_list= []

for request in driver.requests:
    # 바이어 리스트 관련 정보만 필터링
    if request.response and request.url == 'https://www.ksure.or.kr:8443/research/buyer/selectBuyerList.do':
        # Print the response
        # 리스폰스를 디코드해줘야지 정상적으로 나옴.
        json_response = request.response.body.decode('utf-8')

        new_data = json.loads(json_response)
        
        # Check for duplicates before adding to the list
        if new_data not in request_list:
            request_list.append(new_data)

with open(f'Buyer_list_{nation_name}.json', 'w') as f:
    json.dump(request_list, f, ensure_ascii=False, indent=1)
