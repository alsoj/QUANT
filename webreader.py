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
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&orderStat=D', header=0)[0]

    # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

    # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
    code_df = code_df[['회사명', '종목코드']]

    # 한글로된 컬럼명을 영어로 바꿔준다.
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    return code_df

# 주가 데이터 크롤링 from 네이버 금융
def get_stock_history(code, pageNum):
    """
    크롤링 결과 예시
    일자 : <td align="center"><span class="tah p10 gray03">2020.05.26</span></td>
    종가 : <td class="num"><span class="tah p11">44,800</span></td>
    전일비 : <td class="num"><span class="tah p11 red02">1,050</span></td>
    시가 : <td class="num"><span class="tah p11">43,450</span></td>
    고가 : <td class="num"><span class="tah p11">45,150</span></td>
    저가 : <td class="num"><span class="tah p11">43,400</span></td>
    거래량 : <td class="num"><span class="tah p11">69,812</span></td>

    """
    stockHistory = []
    for i in range(pageNum+1):
        print("주가 데이터 크롤링 : {} 진행 중".format(pageNum-i))
        url = "https://finance.naver.com/item/sise_day.nhn?code={}&page={}".format(code, pageNum-i)
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html5lib")

        date = soup.findAll('span', attrs={'class':'p10'})
        price = soup.findAll('span', attrs={'class':'p11'})

        for j in range(len(date)):
            dayResult = []
            dayResult.append(date[j].text.strip().replace(".", "")) # 일자
            dayResult.append(price[6*j].text.strip().replace(",", "")) # 종가
            dayResult.append("+" + price[6 * j+1].text.strip().replace(",", "")
                             if "red" in str(price[6 * j+1]) else
                             "-" + price[6 * j+1].text.strip().replace(",", "")) # 전일비
            dayResult.append(price[6 * j+2].text.strip().replace(",", "")) # 시가
            dayResult.append(price[6 * j+3].text.strip().replace(",", "")) # 고가
            dayResult.append(price[6 * j+4].text.strip().replace(",", "")) # 저가
            dayResult.append(price[6 * j+5].text.strip().replace(",", "")) # 거래량

            stockHistory.append(dayResult)

            # print("일자 : " + date[j].text.strip().replace(".", ""))
            # print("종가 : " + price[6*j].text.strip().replace(",", ""))
            # print("전일비 : " + "+" + price[6 * j+1].text.strip().replace(",", "")
            #                   if "red" in str(price[6 * j+1]) else
            #                   "전일비 : " + "-" + price[6 * j+1].text.strip().replace(",", ""))
            # print("시가 : " + price[6 * j+2].text.strip().replace(",", ""))
            # print("고가 : " + price[6 * j+3].text.strip().replace(",", ""))
            # print("저가 : " + price[6 * j+4].text.strip().replace(",", ""))
            # print("거래량 : " + price[6 * j+5].text.strip().replace(",", ""))
            # print("/"*50)

    return stockHistory

if __name__ == "__main__":
    print("main start")