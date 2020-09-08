import pymysql

def connect_db():
    return pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01', db='quant', charset='utf8')

class Portfolio():

    def create_portfolio(self, port_nm, assets, start_yymmdd, end_yymmdd, rebalace):
        """
        백테스트용 포트폴리오 생성
        :param port_nm: 포트폴리오 이름
        :param assets: 운영 자산
        :param start_yymmdd: 시작일
        :param end_yymmdd: 종료일
        :param rebalace: 리밸런싱 주기
        """
        conn = connect_db()
        curs = conn.cursor()

        create_portfolio_sql = """
                INSERT INTO PORTFOLIO (PORT_NAME, OPERATING_ASSETS, START_YYMMDD, END_YYMMDD, REBALANCE_CYCLE)  
                VALUES (%s, %s, %s, %s, %s)
            """

        curs.execute(create_portfolio_sql, (port_nm, assets, start_yymmdd, end_yymmdd, rebalace))
        conn.commit()
        conn.close()

    def create_account(self, port_no, assets):
        """
        포트폴리오별 계좌 생성
        :param port_no: 포트폴리오 번호
        :param assets: 운영 자산
        """
        conn = connect_db()
        curs = conn.cursor()

        insert_account_sql = """
                INSERT INTO ACCOUNT (PORT_NO, ASSET, DEPOSIT, EARNINGS, EARNINGS_RATE)  
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                ASSET = %s, DEPOSIT = %s, EARNINGS = 0, EARNINGS_RATE = 0    
            """

        curs.execute(insert_account_sql, (port_no, assets, assets, 0, 0))
        conn.commit()
        conn.close()

    def calc_profit(self, port_no, stock_code, cur_price):
        """
        계좌 수익률 UPDATE
        :param port_no: 포트폴리오 번호
        :param stock_code: 종목 코드
        :param cur_price: 현재가
        """
        conn = connect_db()
        curs = conn.cursor()

        update_account_detail_sql = """
            UPDATE ACCOUNT_DETAIL
            SET EARNINGS_RATE = (%s - PURCHASE_PRICE) / PURCHASE_PRICE * 100
            WHERE PORT_NO = %s
            AND STOCK_CODE = %s   
        """

        # 입력된 현재가에 따라 수익률 재계산
        curs.execute(update_account_detail_sql, (cur_price, port_no, stock_code))


    def buy_stock(self, port_no, yyyymmdd, stock_code, buy_count):
        """
        매수 함수
        :param port_no: 포트폴리오 번호
        :param yyyymmdd: 기준일자
        :param stock_code: 매수 종목
        :param buy_count: 매수량
        """
        conn = connect_db()
        curs = conn.cursor()

        # 매수 가능 예수금 가져오기
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

        # 계좌 상세, 잔고 update(plus)
        insert_account_detail_sql = """
            INSERT INTO ACCOUNT_DETAIL (PORT_NO, STOCK_CODE, STOCK_NAME, BALANCE, EVALUATED_PRICE, PURCHASE_PRICE)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            BALANCE = BALANCE + %s, 
            EVALUATED_PRICE = EVALUATED_PRICE + %s, 
            PURCHASE_PRICE = ((PURCHASE_PRICE * BALANCE) + (%s * %s)) / BALANCE + %s
        """

        # 계좌, 잔고 update(minus)
        update_account_sql = """
            UPDATE ACCOUNT
               SET DEPOSIT = DEPOSIT - %s
             WHERE PORT_NO = %s
        """

        # 종목별 매수금액 계산
        curs.execute(select_deposit_sql, (port_no))

        # 기준일자 최신 고가
        curs.execute(select_stock_price_sql, (stock_code, stock_code, yyyymmdd))
        cur_price = curs.fetchone()[0]

        # 종목명 가져오기
        curs.execute(select_stock_name_sql, (stock_code))
        stock_name = curs.fetchone()

        # 매수 - 계좌 상세 테이블에 INSERT/UPDATE
        curs.execute(insert_account_detail_sql,
                     (port_no, stock_code, stock_name, buy_count, buy_count * cur_price, cur_price, buy_count,
                      buy_count * cur_price, buy_count, cur_price, buy_count))

        # 매수 - 수익률 계산
        calc_profit(port_no, stock_code, cur_price)

        # 매수 - 계좌 테이블 잔액 수정
        curs.execute(update_account_sql, (buy_count * cur_price, port_no))

        conn.commit()
        conn.close()

if __name__ == "__main__":

    TEST_PORT_NM = '테스트용'
    TEST_ASSETS = '10000000'
    TEST_START_YYMMDD = '20200101'
    TEST_END_YYMMDD = '20200903'
    TEST_REBALANCE = '1'

    test_portfolio = Portfolio()

    # test_portfolio.create_portfolio(TEST_PORT_NM, TEST_ASSETS, TEST_START_YYMMDD, TEST_END_YYMMDD, TEST_REBALANCE)
    test_portfolio.create_account(1, TEST_ASSETS)