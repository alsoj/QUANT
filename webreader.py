import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import re

pd.set_option('display.expand_frame_repr', False)


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
    """
    stock_history = []
    url = "https://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe=day&count={}&requestType=0".format(code, count)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html5lib")

    data = soup.findAll('item')

    for row in data:
        # 일자별 데이터 세팅 ['20200518', '47950', '49100', '47600', '48800', '20481981']
        daily_history = re.findall(r"[-+]?\d*\.\d+|\d+", str(row))
        stock_history.append(daily_history)

    return stock_history

def get_stock_detail(code):
    print("찾을 종목 code ::: " + code)

    temp_url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}&amp;target=finsum_more'.format(code)
    html = requests.get(temp_url).text

    cookies = requests.get(temp_url).cookies
    print(cookies)

    headers = requests.get(temp_url).headers
    print(headers)

    status_code = requests.get(temp_url).status_code
    print(status_code)

    soup = BeautifulSoup(html, "html.parser")

    # print(soup)

    # 크롤링한 web page 중 ajax에서 전달하는 encparam & id 추출
    soup = str(soup)
    encStartIndex = soup.find('encparam:')
    encparam = soup[encStartIndex+11 : encStartIndex+43]
    idStartIndex = soup.find("id: '")
    id = soup[idStartIndex+5 : idStartIndex+15]

    # print("encparam ::: " + encparam)
    # print("id ::: " + id)

    url = 'https://navercomp.wisereport.co.kr/v2/company/ajax/cF1001.aspx?cmp_cd={}&fin_typ=0&freq_typ=Y&encparam={}&id={}'.format(code, encparam, id)
    print("url ::: " + url)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    print(soup)
    #
    # title = soup.findAll('th', attrs={'class': 'bg txt title'})
    # value = soup.findAll('td', attrs={'class':{'num line','num bgE line','num bgE noline-right'} })
    #
    # print(value[0].text.strip())

    # for i in range(len(title)):
    #     print(title[i].text.strip())


if __name__ == "__main__":
    print("main start")
    # stock_history = get_stock_history('005930', 10)
    # print(stock_history)

    get_stock_detail('005380')