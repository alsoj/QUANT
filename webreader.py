import pymysql
import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import re
from selenium import webdriver
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import json
from pandas import json_normalize

# pandas 출력 세팅
pd.set_option('display.max_row', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)

def get_stock_info_from_dart():
    """
    OPEN DART API를 활용하여 고유번호 데이터를 XML로 저장
    """
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    curs = conn.cursor()
    select_apikey_sql = """SELECT CODE_NM FROM CODE_INFO WHERE CODE_ID = 'API'"""
    curs.execute(select_apikey_sql)
    api_key = curs.fetchone()[0]

    conn.commit()
    conn.close()

    # 회사 고유번호 데이터 XML 파일로 저장
    url = 'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={}'.format(api_key)
    with urlopen(url) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('./assets/data/corp_num')


# 종목 번호로 회사 고유번호 찾기
def find_corp_num(stock_code):
    """
    종목번호로 OPEN DART API 고유번호 찾기
    :param stock_code: 종목번호
    :return: 고유번호
    """
    tree = ET.parse('./assets/data/corp_num/CORPCODE.xml')
    root = tree.getroot()

    for country in root.iter("list"):
        if country.findtext("stock_code") == stock_code:
            return country.findtext("corp_code")

def get_financial_statements_dart(corp_code, yyyy, report_code):
    """
    OPEN DART API를 통해 기업별 재무제표 정보 가져오기
    :param corp_code: 고유번호
    :param yyyy: 사업연도
    :param report_code: 보고서 코드
    :return: 딕셔너리
    """
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    curs = conn.cursor()
    select_apikey_sql = """SELECT CODE_NM FROM CODE_INFO WHERE CODE_ID = 'API'"""
    curs.execute(select_apikey_sql)
    api_key = curs.fetchone()[0]

    conn.commit()
    conn.close()

    url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key={}&corp_code={}&bsns_year={}&reprt_code={}&fs_div=CFS'.format(api_key, corp_code, yyyy, report_code)

    html = requests.get(url).text
    json_result = json.loads(html)

    # print(json_result)

    df = json_normalize(json_result['list'])

    # print(df)

    # 필요 데이터만 추출
    df = df[df['sj_div'].isin(['BS','IS','CIS','CF'])] # 재무상태표, 손익계산서, 포괄손익계산서, 현금흐름표

    disclosure = {}

    # 유동자산
    disclosure['current_assets'] = df.loc[(df['account_id'].isin(['ifrs_CurrentAssets', 'ifrs-full_CurrentAssets']))
                                                    | df['account_nm'].isin(['유동자산']), 'thstrm_amount'].iloc[0]

    # 자산총계
    disclosure['assets'] = df.loc[(df['account_id'].isin(['ifrs_Assets', 'ifrs-full_Assets']))
                                            | df['account_nm'].isin(['자산총계']), 'thstrm_amount'].iloc[0]

    # 유동부채
    disclosure['current_liabilities'] = df.loc[(df['account_id'].isin(['ifrs_CurrentLiabilities', 'ifrs-full_CurrentLiabilities']))
                                                         | df['account_nm'].isin(['유동부채']), 'thstrm_amount'].iloc[0]

    # 부채총계
    disclosure['liabilities'] = df.loc[(df['account_id'].isin(['ifrs_Liabilities', 'ifrs-full_Liabilities']))
                                                 | df['account_nm'].isin(['부채총계']), 'thstrm_amount'].iloc[0]

    # 자본총계
    disclosure['equity'] = df.loc[(df['account_id'].isin(['ifrs_Equity', 'ifrs-full_Equity']))
                                            | df['account_nm'].isin(['자본총계']), 'thstrm_amount'].iloc[0]

    # 매출액
    disclosure['revenue'] = df.loc[(df['account_id'].isin(['ifrs_Revenue', 'ifrs-full_Revenue']))
                                             | df['account_nm'].isin(['매출액']), 'thstrm_amount'].iloc[0]

    # 영업이익
    disclosure['operating_income_loss'] = df.loc[(df['account_id'].isin(['dart_OperatingIncomeLoss', 'dart-full_OperatingIncomeLoss']))
                                                           | df['account_nm'].isin(['영업이익(손실)']), 'thstrm_amount'].iloc[0]

    # 당기순이익
    disclosure['profit_loss'] = df.loc[(df['account_id'].isin(['ifrs_ProfitLoss', 'ifrs-full_ProfitLoss']))
                                                 | df['account_nm'].isin(['당기순이익(손실)']), 'thstrm_amount'].iloc[0]

    # 단위 : 억 원
    disclosure = {key : round(float(value)/100000000, 2) for key, value in disclosure.items()}

    # print(disclosure)

    return disclosure


def get_financial_statements(code):
    # 인증값 추출
    re_enc = re.compile("encparam: '(.*)'", re.IGNORECASE)
    re_id = re.compile("id: '([a-zA-Z0-9]*)' ?", re.IGNORECASE)

    url = "https://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd={}".format(code)
    html = requests.get(url, verify=False).text

    search = re_enc.search(html)
    if search is None:
        return {}
    encparam = re_enc.search(html).group(1)
    encid = re_id.search(html).group(1)

    # 스크래핑
    url = "https://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd={}&fin_typ=0&freq_typ=A&encparam={}&id={}".format(
        code, encparam, encid)
    headers = {"Referer": "HACK"}
    html = requests.get(url, headers=headers, verify=False).text

    soup = BeautifulSoup(html, "html5lib")
    dividend = soup.select("table:nth-of-type(2) tr:nth-of-type(33) td span")
    years = soup.select("table:nth-of-type(2) th")

    dividend_dict = {}
    for i in range(len(dividend)):
        dividend_dict[years[i + 3].text.strip()[:4]] = dividend[i].text

    return dividend_dict


def get_3year_treasury():
    url = "http://www.index.go.kr/strata/jsp/showStblGams3.jsp?stts_cd=288401&amp;idx_cd=2884&amp;freq=Y&amp;period=1998:2018"
    html = requests.get(url, verify=False).text
    soup = BeautifulSoup(html, 'html5lib')
    td_data = soup.select("tr td")

    treasury_3year = {}
    start_year = 1998

    for x in td_data:
        treasury_3year[start_year] = x.text
        start_year += 1

    return treasury_3year


def get_dividend_yield(code):
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd=" + code
    html = requests.get(url, verify=False).text

    soup = BeautifulSoup(html, 'html5lib')
    dt_data = soup.select("td dl dt")

    dividend_yield = dt_data[-2].text
    dividend_yield = dividend_yield.split(' ')[1]
    dividend_yield = dividend_yield[:-1]

    return dividend_yield


def get_estimated_dividend_yield(code):
    dividend_yield = get_financial_statements(code)
    if len(dividend_yield) == 0:
        return 0
    dividend_yield = sorted(dividend_yield.items())[-1]
    return dividend_yield[1]


def get_current_3year_treasury():
    url = "http://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y&page=1"
    html = requests.get(url, verify=False).text

    soup = BeautifulSoup(html, 'html5lib')
    td_data = soup.select("tr td")
    return td_data[1].text


def get_previous_dividend_yield(code):
    dividend_yield = get_financial_statements(code)

    now = datetime.datetime.now()
    cur_year = now.year

    previous_dividend_yield = {}

    for year in range(cur_year - 5, cur_year):
        if str(year) in dividend_yield:
            previous_dividend_yield[year] = dividend_yield[str(year)]

    return previous_dividend_yield

# 상장 기업 종목 코드 가져오기 from 한국거래소
def get_stock_code():
    """
    한국 거래소에 상장된 전체 기업 종목코드 조회
    :return: 회사명, 종목코드가 포함된 데이터프레임
    """

    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&orderStat=D'
    df_code = pd.read_html(url, header=0)[0]

    # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
    df_code.종목코드 = df_code.종목코드.map('{:06d}'.format)

    # 필요한 컬럼만 남김(회사 명과 종목코드)
    df_code = df_code[['회사명', '종목코드']]

    # 한글로 된 컬럼명을 영어로 변경
    df_code = df_code.rename(columns={'회사명': 'name', '종목코드': 'code'})

    return df_code

# 주가 데이터 크롤링 from 네이버 금융
def get_stock_history(code, count):
    """
    크롤링 결과 예시
    <item data="20190314|43700|44300|43550|43850|18039161"> ==> 일자|시가|고가|저가|종가|거래량
    :param code: 종목 코드
    :param count: 가져올 데이터 건 수
    :return: 해당 종목 코드의 일자, 시가, 고가, 저가, 종가, 거래량 데이터
    """
    stock_history = []
    url = "https://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe=day&count={}&requestType=0".format(code, count)
    html = requests.get(url).text
    # soup = BeautifulSoup(html, "html5lib")
    soup = BeautifulSoup(html, "html.parser")
    data = soup.findAll('item')

    for row in data:
        # 일자별 데이터 세팅 ['20200518', '47950', '49100', '47600', '48800', '20481981']
        daily_history = re.findall(r"[-+]?\d*\.\d+|\d+", str(row))
        stock_history.append(daily_history)

    return stock_history

def get_stock_detail(code):
    """
    재무제표 크롤링
    :param code: 종목 코드
    :return: 재무제표 정보 리스트
    """
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(executable_path=r'./assets/chromedriver.exe', chrome_options=options)
    # driver.maximize_window()

    # code = 종목번호
    # base_url = 'https://finance.naver.com/item/coinfo.nhn?code={}&target=finsum_more'.format(code)
    base_url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}'.format(code)

    driver.get(base_url)
    # frmae구조 안에 필요한 데이터가 있기 때문에 해당 데이터를 수집하기 위해서는 frame구조에 들어가야한다.
    # driver.switch_to.frame(driver.find_element_by_id('coinfo_cp'))

    # print(base_url)
    # print(driver.page_source)

    # 재무제표 "연간" 클릭하기
    driver.find_elements_by_xpath('//*[@class="schtab"][1]/tbody/tr/td[3]')[0].click()

    html0 = driver.page_source
    html1 = BeautifulSoup(html0, 'html.parser')

    html22 = html1.find('table', {'class': 'gHead01 all-width', 'summary': '주요재무정보를 제공합니다.'})

    # date scrapy
    thead0 = html22.find('thead')
    tr0 = thead0.find_all('tr')[1]
    th0 = tr0.find_all('th')

    date = []
    for i in range(len(th0)):
        date.append(''.join(re.findall('[0-9/]', th0[i].text.replace("/",""))))

    # main scrapy
    tbody0 = html22.find('tbody')
    tr0 = tbody0.find_all('tr')
    td = []
    for j in range(len(tr0)):
        td0 = tr0[j].find_all('td')
        td1 = []
        for k in range(len(td0)):
            if td0[k].text == '' or td0[k].text == 'N/A' :
                td1.append('0')
            else:
                td1.append(td0[k].text.replace(",", ""))

        td.append(td1)

    result = list(map(list, zip(date, *td)))
    driver.quit()

    return result


if __name__ == "__main__":
    print("main start")


    # get_stock_info_from_dart()

    # get_financial_statements_dart('00113410', '2019', '11011')
    # get_financial_statements_dart('00126380', '2018', '11011')
    # get_financial_statements_dart('00112378', '2017', '11012')
    # stock_history = get_stock_history('005930', 10)
    # print(stock_history)

    # result = get_stock_detail('005380')
    # print(result)