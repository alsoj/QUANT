/*********************
0.각종 코드 테이블 생성
*********************/
DROP TABLE `CODE_INFO`;
CREATE TABLE `CODE_INFO` (
  `CODE_ID` varchar(10) NOT NULL COMMENT '코드 ID',
  `CODE_NM` varchar(50) NOT NULL COMMENT '코드 명',
  `USE_YN` VARCHAR(1) DEFAULT NULL COMMENT '사용여부',
  PRIMARY KEY (`CODE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


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
2.종목 정보 테이블 생성
*********************/
DROP TABLE `STOCK_INFO`;
CREATE TABLE `STOCK_INFO` (
  `stock_code` varchar(10) NOT NULL COMMENT '종목 코드',
  `stock_name` varchar(200) DEFAULT NULL COMMENT '종목명',
  `stock_type` varchar(20) DEFAULT NULL COMMENT '종목 타입',
  `corp_code` varchar(10) DEFAULT NULL COMMENT '고유번호',
  `kor_yn` varchar(1) DEFAULT NULL COMMENT '본사 국내 여부',
  `holdings_yn` varchar(1) DEFAULT NULL COMMENT '지주사 여부',
  `finance_yn` varchar(1) DEFAULT NULL COMMENT '금융사 여부',
  `spac_yn` varchar(1) DEFAULT NULL COMMENT '스팩 여부',
  `use_yn` varchar(1) DEFAULT '1' COMMENT '사용 여부',
  PRIMARY KEY (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



/*********************
3.종목 상세(재무정보) 테이블 생성
*********************/
DROP TABLE `STOCK_DETAIL`;
CREATE TABLE `STOCK_DETAIL` (
  `stock_code` varchar(10) NOT NULL COMMENT '종목 코드',
  `date` varchar(10) NOT NULL COMMENT '일자',
  `detail_1` float DEFAULT NULL COMMENT '매출액',
  `detail_2` float DEFAULT NULL COMMENT '영업이익',
  `detail_3` float DEFAULT NULL COMMENT '영업이익(발표기준)',
  `detail_4` float DEFAULT NULL COMMENT '세전계속사업이익',
  `detail_5` float DEFAULT NULL COMMENT '당기순이익',
  `detail_6` float DEFAULT NULL COMMENT '당기순이익(지배)',
  `detail_7` float DEFAULT NULL COMMENT '당기순이익(비지배)',
  `detail_8` float DEFAULT NULL COMMENT '자산총계',
  `detail_9` float DEFAULT NULL COMMENT '부채총계',
  `detail_10` float DEFAULT NULL COMMENT '자본총계',
  `detail_11` float DEFAULT NULL COMMENT '자본총계(지배)',
  `detail_12` float DEFAULT NULL COMMENT '자본총계(비지배)',
  `detail_13` float DEFAULT NULL COMMENT '자본금',
  `detail_14` float DEFAULT NULL COMMENT '영업활동현금흐름',
  `detail_15` float DEFAULT NULL COMMENT '투자활동현금흐름',
  `detail_16` float DEFAULT NULL COMMENT '재무활동현금흐름',
  `detail_17` float DEFAULT NULL COMMENT 'CAPEX',
  `detail_18` float DEFAULT NULL COMMENT 'FCF',
  `detail_19` float DEFAULT NULL COMMENT '이자발생부채',
  `detail_20` float DEFAULT NULL COMMENT '영업이익률',
  `detail_21` float DEFAULT NULL COMMENT '순이익률',
  `detail_22` float DEFAULT NULL COMMENT 'ROE(%)',
  `detail_23` float DEFAULT NULL COMMENT 'ROA(%)',
  `detail_24` float DEFAULT NULL COMMENT '부채비율',
  `detail_25` float DEFAULT NULL COMMENT '자본유보율',
  `detail_26` float DEFAULT NULL COMMENT 'EPS(원)',
  `detail_27` float DEFAULT NULL COMMENT 'PER(배)',
  `detail_28` float DEFAULT NULL COMMENT 'BPS(원)',
  `detail_29` float DEFAULT NULL COMMENT 'PBR(배)',
  `detail_30` float DEFAULT NULL COMMENT '현금DPS(원)',
  `detail_31` float DEFAULT NULL COMMENT '현금배당수익률',
  `detail_32` float DEFAULT NULL COMMENT '현금배당성향(%)',
  `detail_33` float DEFAULT NULL COMMENT '발행주식수(보통주)',
  PRIMARY KEY (`stock_code`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*********************
4.계좌 테이블 생성
*********************/
DROP TABLE `ACCOUNT`;
CREATE TABLE `ACCOUNT` (
	`PORT_NO` int(10) NOT NULL COMMENT '포트폴리오 넘버',
	`ASSET` float NOT NULL COMMENT '총자산',
    `DEPOSIT` float NULL COMMENT '예수금',
	`EARNINGS` float NULL COMMENT '손익',
	`EARNINGS_RATE` float NULL COMMENT '수익률',
	PRIMARY KEY (`PORT_NO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*********************
5.계좌 상세 테이블 생성
*********************/
DROP TABLE `ACCOUNT_DETAIL`;
CREATE TABLE `ACCOUNT_DETAIL` (
	`PORT_NO` int(10) NOT NULL COMMENT '포트폴리오 넘버',
	`STOCK_CODE` varchar(10) NOT NULL COMMENT '종목 코드',
	`STOCK_NAME` varchar(200) DEFAULT NULL COMMENT '종목명',
	`EARNINGS` float DEFAULT NULL COMMENT '평가손익',
    `EARNINGS_RATE` float DEFAULT NULL COMMENT '수익률',
    `BALANCE` int(10) DEFAULT NULL COMMENT '잔고',
    `EVALUATED_PRICE` float DEFAULT NULL COMMENT '평가금액',
    `PURCHASE_PRICE` float DEFAULT NULL COMMENT '매입가',
    `PRESENT_PRICE` float DEFAULT NULL COMMENT '현재가',
	PRIMARY KEY (`PORT_NO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*********************
6.STOCK 분봉 테이블 생성
*********************/
DROP TABLE `STOCK_MINUTE_PRICE`;
CREATE TABLE `STOCK_MINUTE_PRICE` (
	`STOCK_CODE` varchar(10) NOT NULL COMMENT '종목 코드',
	`DATE` varchar(20) NOT NULL COMMENT '체결 시간',
	`CLOSE` float DEFAULT NULL COMMENT '현재가',
    `OPEN` float DEFAULT NULL COMMENT '시가',
    `HIGH` float DEFAULT NULL COMMENT '고가',
    `LOW` float DEFAULT NULL COMMENT '저가',
    `VOLUME` float DEFAULT NULL COMMENT '거래량',
	PRIMARY KEY (`STOCK_CODE`, `DATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;