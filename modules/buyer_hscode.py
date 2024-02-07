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
import pandas as pd

options = webdriver.ChromeOptions()

getNationLst = [
        {
            "trgtpsnCd": "012",
            "trgtpsnAbbrNm": "CURACAO"
        },
        {
            "trgtpsnCd": "013",
            "trgtpsnAbbrNm": "생마르탱"
        },
        {
            "trgtpsnCd": "014",
            "trgtpsnAbbrNm": "생바르텔레미"
        },
        {
            "trgtpsnCd": "100",
            "trgtpsnAbbrNm": "대한민국"
        },
        {
            "trgtpsnCd": "104",
            "trgtpsnAbbrNm": "북한"
        },
        {
            "trgtpsnCd": "110",
            "trgtpsnAbbrNm": "아프가니스탄"
        },
        {
            "trgtpsnCd": "115",
            "trgtpsnAbbrNm": "방글라데시"
        },
        {
            "trgtpsnCd": "116",
            "trgtpsnAbbrNm": "부탄"
        },
        {
            "trgtpsnCd": "117",
            "trgtpsnAbbrNm": "미얀마"
        },
        {
            "trgtpsnCd": "118",
            "trgtpsnAbbrNm": "브루나이"
        },
        {
            "trgtpsnCd": "120",
            "trgtpsnAbbrNm": "대만"
        },
        {
            "trgtpsnCd": "121",
            "trgtpsnAbbrNm": "중국"
        },
        {
            "trgtpsnCd": "125",
            "trgtpsnAbbrNm": "괌"
        },
        {
            "trgtpsnCd": "130",
            "trgtpsnAbbrNm": "홍콩"
        },
        {
            "trgtpsnCd": "135",
            "trgtpsnAbbrNm": "인도"
        },
        {
            "trgtpsnCd": "136",
            "trgtpsnAbbrNm": "인도네시아"
        },
        {
            "trgtpsnCd": "137",
            "trgtpsnAbbrNm": "영국령 인도양지역"
        },
        {
            "trgtpsnCd": "140",
            "trgtpsnAbbrNm": "일본"
        },
        {
            "trgtpsnCd": "145",
            "trgtpsnAbbrNm": "라오스"
        },
        {
            "trgtpsnCd": "150",
            "trgtpsnAbbrNm": "마카오"
        },
        {
            "trgtpsnCd": "151",
            "trgtpsnAbbrNm": "말레이시아"
        },
        {
            "trgtpsnCd": "152",
            "trgtpsnAbbrNm": "몰디브"
        },
        {
            "trgtpsnCd": "153",
            "trgtpsnAbbrNm": "북마리아나 군도"
        },
        {
            "trgtpsnCd": "154",
            "trgtpsnAbbrNm": "몽골"
        },
        {
            "trgtpsnCd": "155",
            "trgtpsnAbbrNm": "네팔"
        },
        {
            "trgtpsnCd": "160",
            "trgtpsnAbbrNm": "파키스탄"
        },
        {
            "trgtpsnCd": "165",
            "trgtpsnAbbrNm": "필리핀"
        },
        {
            "trgtpsnCd": "170",
            "trgtpsnAbbrNm": "시킴"
        },
        {
            "trgtpsnCd": "171",
            "trgtpsnAbbrNm": "싱가포르"
        },
        {
            "trgtpsnCd": "175",
            "trgtpsnAbbrNm": "스리랑카"
        },
        {
            "trgtpsnCd": "176",
            "trgtpsnAbbrNm": "베트남"
        },
        {
            "trgtpsnCd": "180",
            "trgtpsnAbbrNm": "태국"
        },
        {
            "trgtpsnCd": "181",
            "trgtpsnAbbrNm": "캄보디아"
        },
        {
            "trgtpsnCd": "210",
            "trgtpsnAbbrNm": "바레인"
        },
        {
            "trgtpsnCd": "215",
            "trgtpsnAbbrNm": "사이프러스"
        },
        {
            "trgtpsnCd": "220",
            "trgtpsnAbbrNm": "이란"
        },
        {
            "trgtpsnCd": "221",
            "trgtpsnAbbrNm": "이라크"
        },
        {
            "trgtpsnCd": "223",
            "trgtpsnAbbrNm": "이스라엘"
        },
        {
            "trgtpsnCd": "230",
            "trgtpsnAbbrNm": "요르단"
        },
        {
            "trgtpsnCd": "235",
            "trgtpsnAbbrNm": "쿠웨이트"
        },
        {
            "trgtpsnCd": "240",
            "trgtpsnAbbrNm": "레바논"
        },
        {
            "trgtpsnCd": "245",
            "trgtpsnAbbrNm": "오만"
        },
        {
            "trgtpsnCd": "248",
            "trgtpsnAbbrNm": "팔레스타인"
        },
        {
            "trgtpsnCd": "250",
            "trgtpsnAbbrNm": "카타르"
        },
        {
            "trgtpsnCd": "255",
            "trgtpsnAbbrNm": "사우디 아라비아"
        },
        {
            "trgtpsnCd": "259",
            "trgtpsnAbbrNm": "시리아"
        },
        {
            "trgtpsnCd": "275",
            "trgtpsnAbbrNm": "튀르키예(구 터키)"
        },
        {
            "trgtpsnCd": "280",
            "trgtpsnAbbrNm": "아랍 에미리트 연합"
        },
        {
            "trgtpsnCd": "285",
            "trgtpsnAbbrNm": "예멘"
        },
        {
            "trgtpsnCd": "305",
            "trgtpsnAbbrNm": "알바니아"
        },
        {
            "trgtpsnCd": "306",
            "trgtpsnAbbrNm": "아르메니아"
        },
        {
            "trgtpsnCd": "307",
            "trgtpsnAbbrNm": "아제르바이잔"
        },
        {
            "trgtpsnCd": "310",
            "trgtpsnAbbrNm": "안도라"
        },
        {
            "trgtpsnCd": "311",
            "trgtpsnAbbrNm": "오스트리아"
        },
        {
            "trgtpsnCd": "312",
            "trgtpsnAbbrNm": "크로아티아"
        },
        {
            "trgtpsnCd": "313",
            "trgtpsnAbbrNm": "보스니아-헤르체코비나"
        },
        {
            "trgtpsnCd": "314",
            "trgtpsnAbbrNm": "불가리아"
        },
        {
            "trgtpsnCd": "315",
            "trgtpsnAbbrNm": "벨기에"
        },
        {
            "trgtpsnCd": "316",
            "trgtpsnAbbrNm": "벨라루스"
        },
        {
            "trgtpsnCd": "317",
            "trgtpsnAbbrNm": "덴마크"
        },
        {
            "trgtpsnCd": "318",
            "trgtpsnAbbrNm": "체코"
        },
        {
            "trgtpsnCd": "319",
            "trgtpsnAbbrNm": "슬로바키아"
        },
        {
            "trgtpsnCd": "320",
            "trgtpsnAbbrNm": "핀란드"
        },
        {
            "trgtpsnCd": "321",
            "trgtpsnAbbrNm": "프랑스"
        },
        {
            "trgtpsnCd": "322",
            "trgtpsnAbbrNm": "에스토니아"
        },
        {
            "trgtpsnCd": "323",
            "trgtpsnAbbrNm": "조지아"
        },
        {
            "trgtpsnCd": "325",
            "trgtpsnAbbrNm": "독일"
        },
        {
            "trgtpsnCd": "326",
            "trgtpsnAbbrNm": "지브랄타"
        },
        {
            "trgtpsnCd": "327",
            "trgtpsnAbbrNm": "그리스"
        },
        {
            "trgtpsnCd": "328",
            "trgtpsnAbbrNm": "헝가리"
        },
        {
            "trgtpsnCd": "329",
            "trgtpsnAbbrNm": "그린랜드"
        },
        {
            "trgtpsnCd": "330",
            "trgtpsnAbbrNm": "아이슬란드"
        },
        {
            "trgtpsnCd": "331",
            "trgtpsnAbbrNm": "아일랜드"
        },
        {
            "trgtpsnCd": "332",
            "trgtpsnAbbrNm": "이탈리아"
        },
        {
            "trgtpsnCd": "333",
            "trgtpsnAbbrNm": "카자흐스탄"
        },
        {
            "trgtpsnCd": "334",
            "trgtpsnAbbrNm": "키르기즈스탄"
        },
        {
            "trgtpsnCd": "335",
            "trgtpsnAbbrNm": "맨섬"
        },
        {
            "trgtpsnCd": "338",
            "trgtpsnAbbrNm": "리히텐슈타인"
        },
        {
            "trgtpsnCd": "339",
            "trgtpsnAbbrNm": "라트비아"
        },
        {
            "trgtpsnCd": "340",
            "trgtpsnAbbrNm": "룩셈부르크"
        },
        {
            "trgtpsnCd": "341",
            "trgtpsnAbbrNm": "리투아니아"
        },
        {
            "trgtpsnCd": "343",
            "trgtpsnAbbrNm": "북마케도니아"
        },
        {
            "trgtpsnCd": "345",
            "trgtpsnAbbrNm": "몰타"
        },
        {
            "trgtpsnCd": "346",
            "trgtpsnAbbrNm": "몰도바"
        },
        {
            "trgtpsnCd": "347",
            "trgtpsnAbbrNm": "모나코"
        },
        {
            "trgtpsnCd": "349",
            "trgtpsnAbbrNm": "네덜란드"
        },
        {
            "trgtpsnCd": "350",
            "trgtpsnAbbrNm": "노르웨이"
        },
        {
            "trgtpsnCd": "351",
            "trgtpsnAbbrNm": "폴란드"
        },
        {
            "trgtpsnCd": "352",
            "trgtpsnAbbrNm": "포르투갈"
        },
        {
            "trgtpsnCd": "353",
            "trgtpsnAbbrNm": "루마니아"
        },
        {
            "trgtpsnCd": "354",
            "trgtpsnAbbrNm": "산마리노"
        },
        {
            "trgtpsnCd": "355",
            "trgtpsnAbbrNm": "스페인"
        },
        {
            "trgtpsnCd": "356",
            "trgtpsnAbbrNm": "세르비아"
        },
        {
            "trgtpsnCd": "357",
            "trgtpsnAbbrNm": "스웨덴"
        },
        {
            "trgtpsnCd": "358",
            "trgtpsnAbbrNm": "스위스"
        },
        {
            "trgtpsnCd": "360",
            "trgtpsnAbbrNm": "영국"
        },
        {
            "trgtpsnCd": "361",
            "trgtpsnAbbrNm": "러시아"
        },
        {
            "trgtpsnCd": "362",
            "trgtpsnAbbrNm": "바티칸"
        },
        {
            "trgtpsnCd": "363",
            "trgtpsnAbbrNm": "차넬아일랜드(JERSEY)"
        },
        {
            "trgtpsnCd": "364",
            "trgtpsnAbbrNm": "타지키스탄"
        },
        {
            "trgtpsnCd": "365",
            "trgtpsnAbbrNm": "투르크메니스탄"
        },
        {
            "trgtpsnCd": "366",
            "trgtpsnAbbrNm": "우크라이나"
        },
        {
            "trgtpsnCd": "367",
            "trgtpsnAbbrNm": "우즈베키스탄"
        },
        {
            "trgtpsnCd": "368",
            "trgtpsnAbbrNm": "차넬아일랜드(GUERNSEY)"
        },
        {
            "trgtpsnCd": "370",
            "trgtpsnAbbrNm": "슬로베니아"
        },
        {
            "trgtpsnCd": "371",
            "trgtpsnAbbrNm": "알랜드아일랜드"
        },
        {
            "trgtpsnCd": "372",
            "trgtpsnAbbrNm": "스발바드"
        },
        {
            "trgtpsnCd": "373",
            "trgtpsnAbbrNm": "잔메이엔"
        },
        {
            "trgtpsnCd": "375",
            "trgtpsnAbbrNm": "몬테네그로"
        },
        {
            "trgtpsnCd": "376",
            "trgtpsnAbbrNm": "코소보"
        },
        {
            "trgtpsnCd": "410",
            "trgtpsnAbbrNm": "캐나다"
        },
        {
            "trgtpsnCd": "450",
            "trgtpsnAbbrNm": "미국"
        },
        {
            "trgtpsnCd": "490",
            "trgtpsnAbbrNm": "세인트 피에르 미켈론"
        },
        {
            "trgtpsnCd": "501",
            "trgtpsnAbbrNm": "앵귈라"
        },
        {
            "trgtpsnCd": "503",
            "trgtpsnAbbrNm": "아르헨티나"
        },
        {
            "trgtpsnCd": "504",
            "trgtpsnAbbrNm": "앤티가 바부다"
        },
        {
            "trgtpsnCd": "505",
            "trgtpsnAbbrNm": "아루바"
        },
        {
            "trgtpsnCd": "506",
            "trgtpsnAbbrNm": "영국령 버진군도"
        },
        {
            "trgtpsnCd": "507",
            "trgtpsnAbbrNm": "바하마"
        },
        {
            "trgtpsnCd": "508",
            "trgtpsnAbbrNm": "바베이도스"
        },
        {
            "trgtpsnCd": "509",
            "trgtpsnAbbrNm": "버뮤다"
        },
        {
            "trgtpsnCd": "510",
            "trgtpsnAbbrNm": "볼리비아"
        },
        {
            "trgtpsnCd": "511",
            "trgtpsnAbbrNm": "브라질"
        },
        {
            "trgtpsnCd": "512",
            "trgtpsnAbbrNm": "벨리즈"
        },
        {
            "trgtpsnCd": "513",
            "trgtpsnAbbrNm": "케이만군도"
        },
        {
            "trgtpsnCd": "514",
            "trgtpsnAbbrNm": "아조레스"
        },
        {
            "trgtpsnCd": "516",
            "trgtpsnAbbrNm": "칠레"
        },
        {
            "trgtpsnCd": "517",
            "trgtpsnAbbrNm": "콜롬비아"
        },
        {
            "trgtpsnCd": "518",
            "trgtpsnAbbrNm": "코스타리카"
        },
        {
            "trgtpsnCd": "519",
            "trgtpsnAbbrNm": "쿠바"
        },
        {
            "trgtpsnCd": "520",
            "trgtpsnAbbrNm": "도미니카공화국"
        },
        {
            "trgtpsnCd": "521",
            "trgtpsnAbbrNm": "도미니카 연방"
        },
        {
            "trgtpsnCd": "525",
            "trgtpsnAbbrNm": "에콰도르"
        },
        {
            "trgtpsnCd": "527",
            "trgtpsnAbbrNm": "엘살바도르"
        },
        {
            "trgtpsnCd": "528",
            "trgtpsnAbbrNm": "포크랜드 군도"
        },
        {
            "trgtpsnCd": "529",
            "trgtpsnAbbrNm": "프랑스령 가이아나"
        },
        {
            "trgtpsnCd": "530",
            "trgtpsnAbbrNm": "과테말라"
        },
        {
            "trgtpsnCd": "531",
            "trgtpsnAbbrNm": "그레나다"
        },
        {
            "trgtpsnCd": "532",
            "trgtpsnAbbrNm": "과달루프"
        },
        {
            "trgtpsnCd": "534",
            "trgtpsnAbbrNm": "가이아나"
        },
        {
            "trgtpsnCd": "540",
            "trgtpsnAbbrNm": "아이티"
        },
        {
            "trgtpsnCd": "542",
            "trgtpsnAbbrNm": "온두라스"
        },
        {
            "trgtpsnCd": "544",
            "trgtpsnAbbrNm": "자메이카"
        },
        {
            "trgtpsnCd": "547",
            "trgtpsnAbbrNm": "말티니크"
        },
        {
            "trgtpsnCd": "548",
            "trgtpsnAbbrNm": "몬트세라트"
        },
        {
            "trgtpsnCd": "550",
            "trgtpsnAbbrNm": "멕시코"
        },
        {
            "trgtpsnCd": "552",
            "trgtpsnAbbrNm": "니카라과"
        },
        {
            "trgtpsnCd": "557",
            "trgtpsnAbbrNm": "파나마"
        },
        {
            "trgtpsnCd": "558",
            "trgtpsnAbbrNm": "파라과이"
        },
        {
            "trgtpsnCd": "560",
            "trgtpsnAbbrNm": "페루"
        },
        {
            "trgtpsnCd": "562",
            "trgtpsnAbbrNm": "푸에르토 리코"
        },
        {
            "trgtpsnCd": "563",
            "trgtpsnAbbrNm": "세인트 키츠 네비스"
        },
        {
            "trgtpsnCd": "566",
            "trgtpsnAbbrNm": "세인트 루시아"
        },
        {
            "trgtpsnCd": "570",
            "trgtpsnAbbrNm": "수리남"
        },
        {
            "trgtpsnCd": "571",
            "trgtpsnAbbrNm": "세인트 빈센트 그레나딘"
        },
        {
            "trgtpsnCd": "572",
            "trgtpsnAbbrNm": "트리니다드토바고"
        },
        {
            "trgtpsnCd": "573",
            "trgtpsnAbbrNm": "터크스 카이코스군도"
        },
        {
            "trgtpsnCd": "575",
            "trgtpsnAbbrNm": "우루과이"
        },
        {
            "trgtpsnCd": "580",
            "trgtpsnAbbrNm": "베네수엘라"
        },
        {
            "trgtpsnCd": "581",
            "trgtpsnAbbrNm": "미국령 버진군도"
        },
        {
            "trgtpsnCd": "582",
            "trgtpsnAbbrNm": "나바사섬"
        },
        {
            "trgtpsnCd": "602",
            "trgtpsnAbbrNm": "알제리"
        },
        {
            "trgtpsnCd": "603",
            "trgtpsnAbbrNm": "앙골라"
        },
        {
            "trgtpsnCd": "605",
            "trgtpsnAbbrNm": "베넹"
        },
        {
            "trgtpsnCd": "606",
            "trgtpsnAbbrNm": "보츠와나"
        },
        {
            "trgtpsnCd": "607",
            "trgtpsnAbbrNm": "브룬디"
        },
        {
            "trgtpsnCd": "608",
            "trgtpsnAbbrNm": "코모로"
        },
        {
            "trgtpsnCd": "609",
            "trgtpsnAbbrNm": "남수단"
        },
        {
            "trgtpsnCd": "610",
            "trgtpsnAbbrNm": "카메룬"
        },
        {
            "trgtpsnCd": "611",
            "trgtpsnAbbrNm": "카나리 군도"
        },
        {
            "trgtpsnCd": "612",
            "trgtpsnAbbrNm": "카보베르데"
        },
        {
            "trgtpsnCd": "613",
            "trgtpsnAbbrNm": "중앙아프리카공화국"
        },
        {
            "trgtpsnCd": "614",
            "trgtpsnAbbrNm": "차드"
        },
        {
            "trgtpsnCd": "615",
            "trgtpsnAbbrNm": "콩고"
        },
        {
            "trgtpsnCd": "616",
            "trgtpsnAbbrNm": "코트디부아르"
        },
        {
            "trgtpsnCd": "617",
            "trgtpsnAbbrNm": "지부티"
        },
        {
            "trgtpsnCd": "618",
            "trgtpsnAbbrNm": "이집트"
        },
        {
            "trgtpsnCd": "619",
            "trgtpsnAbbrNm": "적도기니"
        },
        {
            "trgtpsnCd": "620",
            "trgtpsnAbbrNm": "에티오피아"
        },
        {
            "trgtpsnCd": "621",
            "trgtpsnAbbrNm": "에리트리아"
        },
        {
            "trgtpsnCd": "623",
            "trgtpsnAbbrNm": "부르키나파소"
        },
        {
            "trgtpsnCd": "625",
            "trgtpsnAbbrNm": "가봉"
        },
        {
            "trgtpsnCd": "626",
            "trgtpsnAbbrNm": "감비아"
        },
        {
            "trgtpsnCd": "627",
            "trgtpsnAbbrNm": "가나"
        },
        {
            "trgtpsnCd": "628",
            "trgtpsnAbbrNm": "기니"
        },
        {
            "trgtpsnCd": "629",
            "trgtpsnAbbrNm": "기니비사우"
        },
        {
            "trgtpsnCd": "630",
            "trgtpsnAbbrNm": "케냐"
        },
        {
            "trgtpsnCd": "635",
            "trgtpsnAbbrNm": "레소토"
        },
        {
            "trgtpsnCd": "636",
            "trgtpsnAbbrNm": "라이베리아"
        },
        {
            "trgtpsnCd": "637",
            "trgtpsnAbbrNm": "리비아"
        },
        {
            "trgtpsnCd": "638",
            "trgtpsnAbbrNm": "마다가스카르"
        },
        {
            "trgtpsnCd": "641",
            "trgtpsnAbbrNm": "말라위"
        },
        {
            "trgtpsnCd": "642",
            "trgtpsnAbbrNm": "말리"
        },
        {
            "trgtpsnCd": "643",
            "trgtpsnAbbrNm": "모리타니아"
        },
        {
            "trgtpsnCd": "644",
            "trgtpsnAbbrNm": "모리셔스"
        },
        {
            "trgtpsnCd": "645",
            "trgtpsnAbbrNm": "모로코"
        },
        {
            "trgtpsnCd": "646",
            "trgtpsnAbbrNm": "모잠비크"
        },
        {
            "trgtpsnCd": "647",
            "trgtpsnAbbrNm": "마요뜨"
        },
        {
            "trgtpsnCd": "650",
            "trgtpsnAbbrNm": "니제르"
        },
        {
            "trgtpsnCd": "651",
            "trgtpsnAbbrNm": "나이지리아"
        },
        {
            "trgtpsnCd": "652",
            "trgtpsnAbbrNm": "나미비아"
        },
        {
            "trgtpsnCd": "655",
            "trgtpsnAbbrNm": "레위니옹"
        },
        {
            "trgtpsnCd": "657",
            "trgtpsnAbbrNm": "남아프리카공화국"
        },
        {
            "trgtpsnCd": "659",
            "trgtpsnAbbrNm": "르완다"
        },
        {
            "trgtpsnCd": "666",
            "trgtpsnAbbrNm": "상투메프린시페"
        },
        {
            "trgtpsnCd": "667",
            "trgtpsnAbbrNm": "세네갈"
        },
        {
            "trgtpsnCd": "668",
            "trgtpsnAbbrNm": "세이셜"
        },
        {
            "trgtpsnCd": "669",
            "trgtpsnAbbrNm": "시에라리온"
        },
        {
            "trgtpsnCd": "670",
            "trgtpsnAbbrNm": "소말리아"
        },
        {
            "trgtpsnCd": "673",
            "trgtpsnAbbrNm": "수단"
        },
        {
            "trgtpsnCd": "674",
            "trgtpsnAbbrNm": "에스와티니"
        },
        {
            "trgtpsnCd": "675",
            "trgtpsnAbbrNm": "세인트헬레나"
        },
        {
            "trgtpsnCd": "680",
            "trgtpsnAbbrNm": "토고"
        },
        {
            "trgtpsnCd": "681",
            "trgtpsnAbbrNm": "튀니지"
        },
        {
            "trgtpsnCd": "683",
            "trgtpsnAbbrNm": "트리스탄 다 쿠냐"
        },
        {
            "trgtpsnCd": "687",
            "trgtpsnAbbrNm": "우간다"
        },
        {
            "trgtpsnCd": "690",
            "trgtpsnAbbrNm": "탄자니아"
        },
        {
            "trgtpsnCd": "691",
            "trgtpsnAbbrNm": "콩고민주공화국"
        },
        {
            "trgtpsnCd": "692",
            "trgtpsnAbbrNm": "잠비아"
        },
        {
            "trgtpsnCd": "694",
            "trgtpsnAbbrNm": "짐바브웨"
        },
        {
            "trgtpsnCd": "695",
            "trgtpsnAbbrNm": "세우타"
        },
        {
            "trgtpsnCd": "696",
            "trgtpsnAbbrNm": "멜리야"
        },
        {
            "trgtpsnCd": "701",
            "trgtpsnAbbrNm": "호주"
        },
        {
            "trgtpsnCd": "702",
            "trgtpsnAbbrNm": "피지"
        },
        {
            "trgtpsnCd": "703",
            "trgtpsnAbbrNm": "뉴질랜드"
        },
        {
            "trgtpsnCd": "704",
            "trgtpsnAbbrNm": "뉴칼레도니아"
        },
        {
            "trgtpsnCd": "705",
            "trgtpsnAbbrNm": "호주남극속령"
        },
        {
            "trgtpsnCd": "706",
            "trgtpsnAbbrNm": "Baker and Howland Islands"
        },
        {
            "trgtpsnCd": "707",
            "trgtpsnAbbrNm": "British Antarctic Territory"
        },
        {
            "trgtpsnCd": "708",
            "trgtpsnAbbrNm": "코랄섬"
        },
        {
            "trgtpsnCd": "709",
            "trgtpsnAbbrNm": "French Southern and Antarctic Territory"
        },
        {
            "trgtpsnCd": "711",
            "trgtpsnAbbrNm": "French Polynesia"
        },
        {
            "trgtpsnCd": "712",
            "trgtpsnAbbrNm": "Heard Island and McDonald Islands"
        },
        {
            "trgtpsnCd": "713",
            "trgtpsnAbbrNm": "미크로네시아"
        },
        {
            "trgtpsnCd": "714",
            "trgtpsnAbbrNm": "자비스섬"
        },
        {
            "trgtpsnCd": "715",
            "trgtpsnAbbrNm": "마리아나 군도"
        },
        {
            "trgtpsnCd": "716",
            "trgtpsnAbbrNm": "킹맨리프"
        },
        {
            "trgtpsnCd": "717",
            "trgtpsnAbbrNm": "Midway Island"
        },
        {
            "trgtpsnCd": "719",
            "trgtpsnAbbrNm": "노르웨이 속령"
        },
        {
            "trgtpsnCd": "720",
            "trgtpsnAbbrNm": "나우루"
        },
        {
            "trgtpsnCd": "721",
            "trgtpsnAbbrNm": "팔미라"
        },
        {
            "trgtpsnCd": "722",
            "trgtpsnAbbrNm": "로스속령"
        },
        {
            "trgtpsnCd": "723",
            "trgtpsnAbbrNm": "웨이크아일랜드"
        },
        {
            "trgtpsnCd": "730",
            "trgtpsnAbbrNm": "팔라우"
        },
        {
            "trgtpsnCd": "732",
            "trgtpsnAbbrNm": "파푸아뉴기니"
        },
        {
            "trgtpsnCd": "740",
            "trgtpsnAbbrNm": "솔로몬제도"
        },
        {
            "trgtpsnCd": "741",
            "trgtpsnAbbrNm": "남조지아남샌드위치군도"
        },
        {
            "trgtpsnCd": "742",
            "trgtpsnAbbrNm": "아쉬모아 카르티어 아일랜드"
        },
        {
            "trgtpsnCd": "743",
            "trgtpsnAbbrNm": "크리스마스 아일랜드"
        },
        {
            "trgtpsnCd": "744",
            "trgtpsnAbbrNm": "코코스 아일랜드"
        },
        {
            "trgtpsnCd": "745",
            "trgtpsnAbbrNm": "노포크 아일랜드"
        },
        {
            "trgtpsnCd": "755",
            "trgtpsnAbbrNm": "통가"
        },
        {
            "trgtpsnCd": "760",
            "trgtpsnAbbrNm": "사모아"
        },
        {
            "trgtpsnCd": "761",
            "trgtpsnAbbrNm": "미국령 사모아"
        },
        {
            "trgtpsnCd": "762",
            "trgtpsnAbbrNm": "투발루"
        },
        {
            "trgtpsnCd": "763",
            "trgtpsnAbbrNm": "쿡제도"
        },
        {
            "trgtpsnCd": "764",
            "trgtpsnAbbrNm": "존스톤 아일랜드"
        },
        {
            "trgtpsnCd": "765",
            "trgtpsnAbbrNm": "키리바시"
        },
        {
            "trgtpsnCd": "766",
            "trgtpsnAbbrNm": "마샬군도"
        },
        {
            "trgtpsnCd": "768",
            "trgtpsnAbbrNm": "니우에"
        },
        {
            "trgtpsnCd": "769",
            "trgtpsnAbbrNm": "피트케안"
        },
        {
            "trgtpsnCd": "770",
            "trgtpsnAbbrNm": "토켈라우"
        },
        {
            "trgtpsnCd": "772",
            "trgtpsnAbbrNm": "바누아투"
        },
        {
            "trgtpsnCd": "774",
            "trgtpsnAbbrNm": "월리스푸트나제도"
        },
        {
            "trgtpsnCd": "781",
            "trgtpsnAbbrNm": "페로아일랜드"
        },
        {
            "trgtpsnCd": "782",
            "trgtpsnAbbrNm": "동티모르"
        }
    ]

def buy_collect(nation_name = '일본', hscode = '070910'):

    example = pd.read_csv('/Users/taewonyun/Documents/GitHub/Prototype/etc/data/csv/istans_hscd.csv')

    example['industy_code'] = example['industy_code'].apply(lambda x: str(x).zfill(5))

    example['hscode'] = example['hscode'].apply(lambda x: str(x).zfill(6))

    industry_code = example[['industy_code','hscode']].set_index('hscode').to_dict()['industy_code'][hscode]

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

    time.sleep(5)
    
    # 국가 검색하는 곳에 국가 검색
    nationNm_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#nationNm"))
    )

    # 국가 이름 설정
    nation_name_ = nation_name

    # 국가 이름 딕트에서 존재하는지 확인하기
    if nation_name_ in [item['trgtpsnAbbrNm'] for item in getNationLst]:
        print(f'{nation_name_}에 대한 정보를 수집합니다.')
    
    else:
        print('국가 이름이 존재하지 않습니다.')
        return 

    # 산업 코드 설정
    industry_code_ = industry_code

    nationNm_element.send_keys(nation_name_)

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
    industry_key = str(industry_code_[:2])

    level1 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//a[@onclick='clickFun2(\"{industry_key}\",\"{raw_data[industry_key]['name']}\",\"{raw_data[industry_key]['index']}\")']"))
    )

    # 엘리먼트를 클릭하거나 다른 작업 수행
    level1.click()

    level2_code = str(industry_code_[:3])

    
    level2 = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#twoStep'))
        )
    
    time.sleep(1)
    
    for tag in level2.find_elements(By.TAG_NAME, "a"):
        onclick_value = tag.get_attribute("onclick")
        if level2_code in onclick_value:
            tag.click()
            break  # 원하는 링크를 찾았으므로 루프 종료

    level3_code = str(industry_code_[:4])

    level3 = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#threeStep'))
        )
    
    time.sleep(1)
    
    for tag in level3.find_elements(By.TAG_NAME, "a"):
        onclick_value = tag.get_attribute("onclick")
        if level3_code in onclick_value:
            tag.click()
            break  # 원하는 링크를 찾았으므로 루프 종료

    level4_code = str(industry_code_[:5])

    level4 = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#fourStep'))
        )
    
    time.sleep(1)

    for tag in level4.find_elements(By.TAG_NAME, "a"):
        onclick_value = tag.get_attribute("onclick")
        if level4_code in onclick_value:
            tag.click()
            break  # 원하는 링크를 찾았으므로 루프 종료

    time.sleep(0.5)

    # 아무 엘레먼트나 클릭해서 엔터키를 누르면 검색이 됨.
    nationNm_element.send_keys(Keys.ENTER)

    time.sleep(1)

    try:
        # 첫 번째 바이어가 나타날 때까지 기다림. 만약 3초 안에 처리하면 바이어가 보통 0명인 경우라 잘 처리해주면 됨.
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pagingId > a.current'))
        )

        if element.text == '0':
            print('바이어가 0건 입니다.')
            driver.quit()
            return

    except TimeoutException:
        # 예외가 발생하면 로딩이 오래 걸린다는 의미이므로 넉넉하게 시간을 다시 줌.
        print('로딩 중')
        element = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#buyerTbody > tr:nth-child(1) > td.t_l'))
        )

    # <em> 태그 안에 있는 내용은 총 n건의 검색 결과에서 n을 가져옴.
    em_element = driver.find_element(By.CSS_SELECTOR, "span.board_total em")

    result_text = em_element.text

    time.sleep(1)

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
            
            # 해당 국가명과 산업코드는 고유한 값으로 해주기 (혹시나 겹칠까봐, 키 이름 바꾸어도 괜찮음)

            for item in request_list:
                for item2 in item:
                    item2['nation_name_unique'] = nation_name_

                    item2['industry_code_unique'] = industry_code_

                    item2['hscode_uid'] = industry_code_

            with open(f'Buyer_list_{nation_name_}_{hscode}.json', 'w') as f:
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

    # 해당 국가명과 산업코드는 고유한 값으로 해주기 (혹시나 겹칠까봐, 키 이름 바꾸어도 괜찮음)
    for item in request_list:
        for item2 in item:
            item2['nation_name_unique'] = nation_name_

            item2['industry_code_unique'] = industry_code_

            item2['hscode_uid'] = industry_code_



    with open(f'Buyer_list_{nation_name_}_{hscode}.json', 'w') as f:
        json.dump(request_list, f, ensure_ascii=False, indent=1)
    
    driver.quit()

if __name__ == '__main__':
    buy_collect()