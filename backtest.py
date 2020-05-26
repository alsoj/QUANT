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


if __name__ == "__main__":
    df_stock_code = webreader.get_stock_code()
    insertStockInfo(df_stock_code)


    # storckHistory = webreader.get_stock_history('307950',1)
    # print(storckHistory)