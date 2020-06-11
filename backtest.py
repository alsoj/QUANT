import pymysql
import webreader

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
    
            """

    # SQL문 실행
    curs.execute(sql)
    undervalued_stock_list = curs.fetchall()
    conn.close()

    return undervalued_stock_list

def checkIsExisted(stock_code):
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
    # df_stock_code = webreader.get_stock_code()
    # insertStockInfo(df_stock_code)

    all_stock_list = select_all_stock_info()

    """
    for stock in all_stock_list:
        # 일별 주가 데이터 가져오기(1주 = 5일, 1년 = 260일, 10년 = 2600일)
        stock_history = webreader.get_stock_history(stock['stock_code'], 2600)
        insert_stock_history(stock['stock_code'], stock_history)
    """
    total_count = len(all_stock_list)
    print("전체 건수 ::: " + str(total_count))
    i = 1
    for stock in all_stock_list:
        print("{}번째 종목 입력 중 ::: {}".format(i, stock['stock_code']))

        # 기존에 입력되지 않은 건들만
        if checkIsExisted(stock['stock_code']) == False:
            try:
                stock_detail = webreader.get_stock_detail(stock['stock_code'])
                insert_stock_detail(stock['stock_code'], stock_detail)
            except:
                print("{} ::: 디테일 INSERT 오류발생".format(str(stock['stock_code'])))
                pass
        i = i + 1

    # storckHistory = webreader.get_stock_history('307950',1)
    # print(storckHistory)