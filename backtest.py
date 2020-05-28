import pymysql
import webreader

def insertStockInfo(df_stock_code):
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

def selectAllStockInfo():
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    # Connection 으로부터 Dictoionary Cursor 생성
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = """select stock_code, stock_name
               from STOCK_INFO
          """

    # SQL문 실행
    curs.execute(sql)

    # 데이타 Fetch
    rows = curs.fetchall()
    for row in rows:
        print(row)
        print(row['stock_code'])
        result = webreader.get_stock_history(row['stock_code'], 10)
        print(result)

        insertStockHistory(row['stock_code'], result)

    conn.close()

def insertStockHistory(stock_code, stock_history):
    conn = pymysql.connect(host='localhost', user='quantadmin', password='quantadmin$01',
                           db='quant', charset='utf8')

    curs = conn.cursor()
    sql = """insert into STOCK_HISTORY(stock_code,date,close,diff,open,high,low,volume)
             values (%s, %s, %s, %s, %s, %s, %s, %s)"""

    for row in stock_history:
        curs.execute(sql, (stock_code, row[0], row[1], row[2], row[3], row[4], row[5], row[6]))


    print("종목 히스토리 INSERT 끝")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # df_stock_code = webreader.get_stock_code()
    # insertStockInfo(df_stock_code)
    selectAllStockInfo()

    # storckHistory = webreader.get_stock_history('307950',1)
    # print(storckHistory)