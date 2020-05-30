/*********************
1.주가 히스토리 테이블 생성
*********************/
DROP TABLE `STOCK_HISTORY`;
CREATE TABLE `STOCK_HISTORY` (
  `stock_code` varchar(10) NOT NULL COMMENT '종목 코드',
  `date` date NOT NULL COMMENT '일자',
  `open` float DEFAULT NULL COMMENT '시가',
  `high` float DEFAULT NULL COMMENT '고가',
  `low` float DEFAULT NULL COMMENT '저가',
  `close` float DEFAULT NULL COMMENT '종가',
  `volume` float DEFAULT NULL COMMENT '거래량',
  PRIMARY KEY (`stock_code`,`date`),
  UNIQUE KEY `idx_TBL_STOCK_HISTORY_stock_code_basic_date` (`date`,`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*********************
1.종목 정보 테이블 생성
*********************/
DROP TABLE `STOCK_INFO`;
CREATE TABLE `STOCK_INFO` (
  `stock_code` varchar(10) NOT NULL COMMENT '종목 코드',
  `stock_name` varchar(200) DEFAULT NULL COMMENT '종목명',
  `stock_type` varchar(10) DEFAULT NULL COMMENT '종목 타입',
  `use_yn` varchar(1) DEFAULT NULL COMMENT '사용 여부',
  PRIMARY KEY (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;