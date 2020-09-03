import pymysql

def connect_db():
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01', db='quant', charset='utf8')

    return conn

class Portfolio():

    def create_portfolio(self, port_nm, assets, start_yymmdd, end_yymmdd, rebalace):
        """
        백테스트용 포트폴리오 생성
        :param port_nm: 포트폴리오 이름
        :param assets: 운용 자산
        :param start_yymmdd: 시작일
        :param end_yymmdd: 종료일
        :param rebalace: 리밸런싱 주기
        :return:
        """
        conn = connect_db()
        curs = conn.cursor()

        insert_account_sql = """
                INSERT INTO PORTFOLIO (PORT_NAME, OPERATING_ASSETS, START_YYMMDD, END_YYMMDD, REBALANCE_CYCLE)  
                VALUES (%s, %s, %s, %s, %s)
            """

        curs.execute(insert_account_sql, (port_nm, assets, start_yymmdd, end_yymmdd, rebalace))
        conn.commit()
        conn.close()

if __name__ == "__main__":

    TEST_PORT_NM = '테스트용'
    TEST_ASSETS = '10000000'
    TEST_START_YYMMDD = '20200101'
    TEST_END_YYMMDD = '20200903'
    TEST_REBALANCE = '1'

    test = Portfolio()

    test.create_portfolio(TEST_PORT_NM, TEST_ASSETS, TEST_START_YYMMDD, TEST_END_YYMMDD, TEST_REBALANCE)