import pymysql
import webreader
import pandas as pd
import os

def insert_stock_info_from_quantking():
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    curs = conn.cursor()
    insert_stock_info_sql = """
        INSERT INTO STOCK_INFO(STOCK_CODE, STOCK_NAME , STOCK_TYPE, KOR_YN, HOLDINGS_YN, FINANCE_YN, SPAC_YN)
             values (%s, %s, %s, %s, %s, %s, %s)"""

    # 현재경로
    # print(os.getcwd())

    df_stock_info = pd.read_excel('./assets/data/stock_info.xlsx')

    for i, row in df_stock_info.iterrows():
        curs.execute(insert_stock_info_sql, (row['종목코드'][1:], row['종목명'], row['업종'], row['국내'], row['지주사'], row['금융사'], row['스팩']))

    conn.commit()
    conn.close()

def update_corp_code():
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    curs = conn.cursor()
    stock_list = select_all_stock_info()

    update_stock_info_sql = """
        UPDATE STOCK_INFO SET CORP_CODE = %s WHERE STOCK_CODE = %s
        """

    print("전체 " + str(len(stock_list)) + "개 기업 중")
    i = 1
    for stock in stock_list:
        print(str(i) + "번 째 입력 중")
        corp_code = webreader.find_corp_num(stock['stock_code'])
        curs.execute(update_stock_info_sql, (corp_code, stock['stock_code']))
        i = i+1

    conn.commit()
    conn.close()


def insert_stock_info(df_stock_code):
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    curs = conn.cursor()
    sql = """insert into STOCK_INFO(stock_code,stock_name,stock_type,use_yn)
             values (%s, %s, %s, %s)"""

    print("종목 정보 INSERT 시작. 전체 건수" + str(len(df_stock_code)))

    for i, row in df_stock_code.iterrows():
        curs.execute(sql, (row['code'], row['name'], '', 'Y'))

        if (i % 100 == 0):
            print("{}번째 완료".format(i))

    print("종목 정보 INSERT 끝")

    conn.commit()
    conn.close()

def select_all_stock_info():
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    # Connection 으로부터 Dictoionary Cursor 생성
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = """select stock_code, stock_name
               from STOCK_INFO
          """

    # SQL문 실행
    curs.execute(sql)
    all_stock_list = curs.fetchall()
    conn.close()

    return all_stock_list

def insert_stock_history(stock_code, stock_history):
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')
    curs = conn.cursor()
    sql = """insert into STOCK_HISTORY(stock_code,date,open,high,low,close,volume)
             values (%s, %s, %s, %s, %s, %s, %s)"""

    for row in stock_history:
        # print(row)
        curs.execute(sql, (stock_code, row[0], row[1], row[2], row[3], row[4], row[5]))

    print("{} ::: 종목 히스토리 INSERT 끝".format(str(stock_code)))

    conn.commit()
    conn.close()

def insert_stock_detail(stock_code, stock_detail):
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')
    curs = conn.cursor()
    sql = """insert into STOCK_DETAIL(stock_code, date, detail_1, detail_2, detail_3, detail_4, detail_5, detail_6,
     detail_7, detail_8, detail_9, detail_10, detail_11, detail_12, detail_13, detail_14, detail_15, detail_16,
     detail_17, detail_18, detail_19, detail_20, detail_21, detail_22, detail_23, detail_24, detail_25, detail_26, 
     detail_27, detail_28, detail_29, detail_30, detail_31, detail_32, detail_33)   
     values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s
           , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
           , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
           , %s, %s, %s, %s, %s)"""

    print("{} ::: 디테일 INSERT 시작".format(str(stock_code)))
    
    for row in stock_detail:
        # print(row)
        curs.execute(sql, (stock_code
                           , row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
                           , row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19]
                           , row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29]
                           , row[30], row[31], row[32], row[33]))

    conn.commit()
    conn.close()

def select_undervalued_stock(yyyymm, topN):
    """
    :param yyyymm:기준연월
    :param topN:추출 종목 수
    :return: undervalued_stock_list
    """
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')
    curs = conn.cursor()
    sql = """
          SELECT DISTINCT STOCK_CODE
            FROM STOCK_DETAIL
           WHERE 1=1
             AND DATE < %s
             AND detail_2 > 0 # 영업이익
             AND detail_22 > 10 # ROE
             AND detail_24 < 100 # 부채비율
             AND detail_31 > 3 # 배당수익률
             AND detail_27 > 0 # PER
             AND detail_27 < 10
             AND detail_29 > 0 # PBR
             AND detail_29 < 0.8
           ORDER BY detail_27
           """

    # SQL문 실행
    curs.execute(sql, (yyyymm))
    undervalued_stock_list = curs.fetchall()
    conn.close()

    return undervalued_stock_list[:topN]

def create_account(port_no, asset):
    """
    백테스트용 계좌 생성
    :param port_no: 포트폴리오 번호
    :param asset: 시작 자산
    :return:
    """
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')
    curs = conn.cursor()

    insert_account_sql = """
        INSERT INTO ACCOUNT (PORT_NO, ASSET, DEPOSIT, EARNINGS, EARNINGS_RATE)  VALUES (%s, %s, %s, 0, 0)
        ON DUPLICATE KEY UPDATE
        ASSET = %s, DEPOSIT = %s, EARNINGS = 0, EARNINGS_RATE = 0    
    """

    curs.execute(insert_account_sql, (port_no, asset, asset, asset, asset))
    conn.commit()
    conn.close()

def buy_stock(port_no, yyyymmdd, stock_list):
    """
    매수 함수
    :param port_no: 포트폴리오 번호
    :param yyyymmdd: 기준일자
    :param stock_list: 매수대상 list
    :return:
    """
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')
    curs = conn.cursor()

    # 매수가능 예수금 가져오기
    select_deposit_sql = """SELECT DEPOSIT FROM ACCOUNT WHERE PORT_NO = %s"""

    # 종목명 가져오기
    select_stock_name_sql = """SELECT STOCK_NAME FROM STOCK_INFO WHERE STOCK_CODE = %s"""

    # 기준일자 주가 가져오기(최신기준 고가)
    select_stock_price_sql = """
        SELECT HIGH 
          FROM STOCK_HISTORY 
         WHERE STOCK_CODE = %s
           AND DATE = (SELECT MAX(DATE) 
                         FROM STOCK_HISTORY 
                        WHERE STOCK_CODE = %s 
                          AND DATE <= %s)
        """

    insert_account_detail_sql = """
        INSERT INTO ACCOUNT_DETAIL (PORT_NO, STOCK_CODE, STOCK_NAME, EARNINGS, EARNINGS_RATE, BALANCE, EVALUATED_PRICE, PURCHASE_PRICE, PRESENT_PRICE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """

    update_account_sql = """
        UPDATE ACCOUNT
           SET DEPOSIT = DEPOSIT - %s
         WHERE PORT_NO = %s
                        """

    # 종목별 매수금액 계산
    curs.execute(select_deposit_sql, (port_no))
    deposit = curs.fetchone()[0]
    buying_amount = int(deposit / len(stock_list))

    for stock_code in stock_list:
        # 기준일자 최신 고가
        curs.execute(select_stock_price_sql, (stock_code, stock_code, yyyymmdd))
        high_price = curs.fetchone()[0]
        
        # 매수량
        balance = int(buying_amount / high_price)

        # 종목명 가져오기
        curs.execute(select_stock_name_sql, (stock_code))
        stock_name = curs.fetchone()

        # 매수 - 계좌 상세 테이블에 INSERT
        curs.execute(insert_account_detail_sql, (port_no, stock_code, stock_name, 0, 0, balance, balance * high_price, high_price, high_price))

        # 매수 - 계좌 테이블 잔액 수정
        curs.execute(update_account_sql, (balance * high_price, port_no))

    conn.commit()
    conn.close()


def check_is_existed(stock_code):
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    # Connection 으로부터 Dictoionary Cursor 생성
    curs = conn.cursor()
    sql = """select count(*) from STOCK_DETAIL where stock_code = %s"""
    curs.execute(sql, (stock_code))

    count = curs.fetchone()
    if int(count[0]) > 0:
        return True
    else:
        return False

if __name__ == "__main__":
    # insert_stock_info_from_quantking()

    update_corp_code()

    # df_stock_code = webreader.get_stock_code()
    # insertStockInfo(df_stock_code)

    # all_stock_list = select_all_stock_info()

    """
    for stock in all_stock_list:
        # 일별 주가 데이터 가져오기(1주 = 5일, 1년 = 260일, 10년 = 2600일)
        stock_history = webreader.get_stock_history(stock['stock_code'], 2600)
        insert_stock_history(stock['stock_code'], stock_history)
    """

    """    
    total_count = len(all_stock_list)
    print("전체 건수 ::: " + str(total_count))
    i = 1
    for stock in all_stock_list:
        print("{}번째 종목 입력 중 ::: {}".format(i, stock['stock_code']))

        # 기존에 입력되지 않은 건들만
        if check_is_existed(stock['stock_code']) == False:
            try:
                stock_detail = webreader.get_stock_detail(stock['stock_code'])
                insert_stock_detail(stock['stock_code'], stock_detail)
            except:
                print("{} ::: 디테일 INSERT 오류발생".format(str(stock['stock_code'])))
                pass
        i = i + 1
    """

    # create_account('00001', '1000000')
    # buy_stock('00001', '20150101', ['005930'])