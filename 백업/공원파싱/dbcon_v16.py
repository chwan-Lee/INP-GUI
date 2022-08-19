import sys
import requests
import json
import csv
import pandas as pd
import pymysql
from tqdm import tqdm
import re
import os

conn = None
cur = None

sql = ""

MAX_sheet = 2  # 시트개수 입력 필수
name = []
park = []
path = "O:/backup_IRSS/data.xlsx"
DBname = "pythonDB"

xl = pd.ExcelFile(path)
res = len(xl.sheet_names)  # 시트 개수

for i in range(0, res):
    dataframeXlsx = pd.read_excel(path, sheet_name=i)  # 데이터를 가져올 엑셀
    for row in dataframeXlsx['ORIG_NAME']:  # 데이터를 가져올 행 이름
        name.append(row)

for i in range(0, res):
    dataframeXlsx = pd.read_excel(path, sheet_name=i)
    for row in dataframeXlsx['DESIG']:
        park.append(row)

park_num = ''
conn = pymysql.connect(host='127.0.0.1', port=3312, user='root', password='!234Qwer', db=DBname, charset='utf8')  # 접속정보
cur = conn.cursor()

for i, j in tqdm(zip(park, name), desc='KCA에서 데이터를 받아오는 중', total=len(name)):

    if i == "국립공원":
        park_num = '1'
    elif i == "도립공원":
        park_num = '2'
    else:
        park_num = '3'

    url = "https://spectrummap.kr/openapiNew.do?key=o65zi311yl5cky28e419&searchId=07&SCH_CD=MOBILE&PARK_CD=" + i + "&QUERY=" + j

    payload = {}
    headers = {
        'Cookie': 'JSESSIONID=543-lEEMcgA_JOMLyCv49-8xAZxwOO5M2FgeEqeN2YPn6yV9ODvA!-980091165'
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)

        js3 = response.text
        jsonObject = json.loads(js3)
        jsonArray = jsonObject.get("RESULT")
    except:
        print("인터넷 연결이 원활하지 않습니다. 확인 후 다시 시도")
        sys.exit(0)

    sql = "DROP TABLE IF EXISTS " + j + "_" + i
    cur.execute(sql)  # 커서로 sql문 실행

    sql = "CREATE TABLE IF NOT EXISTS " + j + "_" + i + " (ID int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY," \
                                                        "`CALL_SIGN` varchar(15) DEFAULT NULL," \
                                                        "`ADDRESS` varchar(50) DEFAULT NULL," \
                                                        "`NETID` varchar(25) DEFAULT NULL," \
                                                        "`TYPE_COORD` varchar(10) DEFAULT NULL," \
                                                        "`COORD_X` double DEFAULT NULL," \
                                                        "`COORD_Y` double DEFAULT NULL," \
                                                        "`ALTITUDE` smallint(6) DEFAULT NULL," \
                                                        "`NOMINAL_POWER` double DEFAULT NULL," \
                                                        "`GAIN` double DEFAULT NULL," \
                                                        "`GAINRX` double DEFAULT NULL," \
                                                        "`LOSSES` double DEFAULT NULL," \
                                                        "`LOSSESRX` double DEFAULT NULL," \
                                                        "`FREQUENCY` double DEFAULT NULL," \
                                                        "`H_ANTENNA` double DEFAULT NULL," \
                                                        "`POLAR` varchar(1) DEFAULT NULL," \
                                                        "`POLARRX` varchar(1) DEFAULT NULL," \
                                                        "`THRESHOLD` double DEFAULT NULL," \
                                                        "`THRESHOLDRX` double DEFAULT NULL," \
                                                        "`BANDWIDTH` double DEFAULT NULL," \
                                                        "`BANDWIDTHRX` double DEFAULT NULL," \
                                                        "`CHANNEL` smallint(6) DEFAULT NULL," \
                                                        "`NB_LINES` smallint(6) DEFAULT NULL," \
                                                        "`TITLE` varchar(25) DEFAULT NULL," \
                                                        "`INFO1` varchar(25) DEFAULT NULL," \
                                                        "`INFO2` varchar(25) DEFAULT NULL," \
                                                        "`INFO3` varchar(25) DEFAULT NULL," \
                                                        "`AZIMUTH` double DEFAULT NULL," \
                                                        "`TILT` double DEFAULT NULL," \
                                                        "`TILTE` double DEFAULT NULL," \
                                                        "`TYPE_ELEMENT` smallint(6) DEFAULT NULL," \
                                                        "`TYPE_STATION` varchar(1) DEFAULT NULL," \
                                                        "`TYPE_LINK` varchar(2) DEFAULT NULL," \
                                                        "`GROUP` varchar(3) DEFAULT NULL," \
                                                        "`DIAG_H` varchar(288) DEFAULT NULL," \
                                                        "`DIAG_V` varchar(716) DEFAULT NULL," \
                                                        "`PROJECT_NAME` varchar(50) DEFAULT NULL," \
                                                        "`Downlink_cx` int(11) DEFAULT NULL," \
                                                        "`Uplink_cx` int(11) DEFAULT NULL," \
                                                        "`D_cx1` double DEFAULT NULL," \
                                                        "`U_cx1` double DEFAULT NULL," \
                                                        "`D_cx2` double DEFAULT NULL," \
                                                        "`U_cx2` double DEFAULT NULL," \
                                                        "`D_cx3` double DEFAULT NULL," \
                                                        "`U_cx3` double DEFAULT NULL," \
                                                        "`D_cx4` double DEFAULT NULL," \
                                                        "`U_cx4` double DEFAULT NULL," \
                                                        "`D_cx5` double DEFAULT NULL," \
                                                        "`U_cx5` double DEFAULT NULL," \
                                                        "`D_cx6` double DEFAULT NULL," \
                                                        "`U_cx6` double DEFAULT NULL," \
                                                        "`D_cx7` double DEFAULT NULL," \
                                                        "`U_cx7` double DEFAULT NULL," \
                                                        "`D_cx8` double DEFAULT NULL," \
                                                        "`U_cx8` double DEFAULT NULL," \
                                                        "`D_cx9` double DEFAULT NULL," \
                                                        "`U_cx9` double DEFAULT NULL," \
                                                        "`D_cx10` double DEFAULT NULL," \
                                                        "`U_cx10` double DEFAULT NULL," \
                                                        "`D_cx11` double DEFAULT NULL," \
                                                        "`U_cx11` double DEFAULT NULL," \
                                                        "`D_cx12` double DEFAULT NULL," \
                                                        "`U_cx12` double DEFAULT NULL," \
                                                        "`D_cx13` double DEFAULT NULL," \
                                                        "`U_cx13` double DEFAULT NULL," \
                                                        "`D_cx14` double DEFAULT NULL," \
                                                        "`U_cx14` double DEFAULT NULL," \
                                                        "`D_cx15` double DEFAULT NULL," \
                                                        "`U_cx15` double DEFAULT NULL," \
                                                        "`D_cx16` double DEFAULT NULL," \
                                                        "`U_cx16` double DEFAULT NULL," \
                                                        "`Spacing` double DEFAULT NULL," \
                                                        "`Category` int(11) DEFAULT NULL," \
                                                        "`CodeSiteA` varchar(9) DEFAULT NULL," \
                                                        "`WiencodeH` varchar(10) DEFAULT NULL," \
                                                        "`WiencodeV` varchar(10) DEFAULT NULL," \
                                                        "`Erlang` double DEFAULT NULL," \
                                                        "`Call_no` double DEFAULT NULL," \
                                                        "`Delay` smallint(6) DEFAULT NULL," \
                                                        "`User` varchar(25) DEFAULT NULL," \
                                                        "`RPE` varchar(50) DEFAULT NULL," \
                                                        "`nfdname` varchar(21) DEFAULT NULL," \
                                                        "`Antenna_nameH` varchar(25) DEFAULT NULL," \
                                                        "`Antenna_nameV` varchar(25) DEFAULT NULL," \
                                                        "`DateServ` double DEFAULT NULL," \
                                                        "`DateBegin` double DEFAULT NULL," \
                                                        "`DateEnd` double DEFAULT NULL," \
                                                        "`LineOffset` smallint(6) DEFAULT NULL," \
                                                        "`Precision` smallint(6) DEFAULT NULL," \
                                                        "`Aperture` float DEFAULT NULL," \
                                                        "`TIL` smallint(6) DEFAULT NULL," \
                                                        "`Modulation` int(11) DEFAULT NULL," \
                                                        "`FKTB` smallint(6) DEFAULT NULL," \
                                                        "`Radius` float DEFAULT NULL," \
                                                        "`THR10_3` float DEFAULT NULL," \
                                                        "`THR10_6` float DEFAULT NULL," \
                                                        "`THR10_8` float DEFAULT NULL," \
                                                        "`THR10_10` float DEFAULT NULL," \
                                                        "`Bit_rate` float DEFAULT NULL," \
                                                        "`Channel_d` varchar(4) DEFAULT NULL," \
                                                        "`Plan` varchar(10) DEFAULT NULL," \
                                                        "`ICS_VALUE` longblob DEFAULT NULL," \
                                                        "`HEFF_VI` varchar(180) DEFAULT NULL," \
                                                        "`HEFF_GE` varchar(180) DEFAULT NULL," \
                                                        "`ICST_STATUS` tinyint(4) DEFAULT NULL," \
                                                        "`POLYGON` varchar(2000) DEFAULT NULL," \
                                                        "`ANT_FILE` varchar(127) DEFAULT NULL," \
                                                        "`Peak_Pow` double DEFAULT NULL," \
                                                        "`OPTIONS` varchar(128) DEFAULT NULL," \
                                                        "`Neighbours` varchar(512) DEFAULT NULL," \
                                                        "`STATION_ID` int(11) DEFAULT NULL," \
                                                        "`Color` int(11) DEFAULT NULL," \
                                                        "`STRINGC` varchar(255) DEFAULT NULL," \
                                                        "`TACLAC` int(11) DEFAULT NULL," \
                                                        "`RSI` varchar(255) DEFAULT NULL," \
                                                        "`MME` varchar(15) DEFAULT NULL," \
                                                        "`SAEGW` varchar(15) DEFAULT NULL," \
                                                        "`PATHCFD` varchar(255) DEFAULT NULL," \
                                                        "`CI_N0` double DEFAULT NULL," \
                                                        "`CI_N1` double DEFAULT NULL," \
                                                        "`RDSPI_SID` int(11) DEFAULT NULL," \
                                                        "`LSN_SWTPI` int(11) DEFAULT NULL," \
                                                        "`TIImain` int(11) DEFAULT NULL," \
                                                        "`TIIsub` int(11) DEFAULT NULL," \
                                                        "`addloss` float DEFAULT NULL," \
                                                        "`PNCODE` int(11) DEFAULT NULL," \
                                                        "`FFFH_TRX` int(11) DEFAULT NULL," \
                                                        "`SPURIOUS` int(11) DEFAULT NULL," \
                                                        "`ETSI_CLASS` varchar(5) DEFAULT NULL," \
                                                        "`SMART` int(11) DEFAULT NULL," \
                                                        "`ARRAYTX` int(11) DEFAULT NULL," \
                                                        "`ARRAYRX` int(11) DEFAULT NULL," \
                                                        "`MU` int(11) DEFAULT NULL," \
                                                        "`ADDPROPLOSSTX` int(11) DEFAULT NULL," \
                                                        "`ADDPROPLOSSRX` int(11) DEFAULT NULL," \
                                                        "`MEAN_FS_MS` float DEFAULT NULL," \
                                                        "`MEAN_FS_MU` float DEFAULT NULL," \
                                                        "`SIGMA_SS` float DEFAULT NULL," \
                                                        "`SIGMA_SU` float DEFAULT NULL," \
                                                        "`Pilot` float DEFAULT NULL," \
                                                        "`Paging` float DEFAULT NULL," \
                                                        "`Sync` float DEFAULT NULL," \
                                                        "`Mchips_s` float DEFAULT NULL," \
                                                        "`PDCCH` float DEFAULT NULL," \
                                                        "`PBCH` float DEFAULT NULL," \
                                                        "`PSS` float DEFAULT NULL," \
                                                        "`SSS` float DEFAULT NULL," \
                                                        "`PowerMaxW` double DEFAULT NULL," \
                                                        "`CHANGE_DATE` double DEFAULT NULL," \
                                                        "`XPD` int(11) DEFAULT NULL," \
                                                        "`SectorBegin` int(11) DEFAULT NULL," \
                                                        "`SectorEnd` int(11) DEFAULT NULL," \
                                                        "`DistSimul` double DEFAULT NULL," \
                                                        "`Pulse` float DEFAULT NULL," \
                                                        "`Rd_Noise` float DEFAULT NULL," \
                                                        "`Det_PD` float DEFAULT NULL," \
                                                        "`Rd_PulseComp` smallint(6) DEFAULT NULL," \
                                                        "`STRING` varchar(255) DEFAULT NULL," \
                                                        "`CHG_DATE` double DEFAULT NULL," \
                                                        "`TLEsatID` float DEFAULT NULL," \
                                                        "`BEAMFORMINGH` int(11) DEFAULT NULL," \
                                                        "`BEAMSTEPH` int(11) DEFAULT NULL," \
                                                        "`BEAMSTEPV` int(11) DEFAULT NULL," \
                                                        "`Numerology` int(11) DEFAULT NULL," \
                                                        "`BEAMFORMINGV` int(11) DEFAULT NULL," \
                                                        "`LAYERS` int(11) DEFAULT NULL," \
                                                        "`RS_Boost` smallint(6) DEFAULT NULL," \
                                                        "`DL_UL` float DEFAULT NULL," \
                                                        "`Activity` smallint(6) DEFAULT NULL," \
                                                        "`STATUS_ELEMENT` smallint(6) DEFAULT NULL," \
                                                        "`RNPC` smallint(6) DEFAULT NULL," \
                                                        "KEY `ID` (`ID`) USING BTREE" \
                                                        ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"

    cur.execute(sql)  # 커서로 sql문 실행

    for list in jsonArray:

        BANDWIDTH = None
        INFO2 = None
        Cate = None
        Pilot = None

        serivce_name = str(list.get("SERVICE_NAME"))  # SERVICE_NAME 을 통해 필요없는 데이터 지우기
        if "IMT-2000" not in serivce_name:
            if "LTE" not in serivce_name:
                # if "5G" not in serivce_name:
                if "Cellular" not in serivce_name:
                    # if "WiBro" not in serivce_name:
                    continue

        try:  # 대역폭과 통신사 데이터 입력
            Mhz = float(list.get("FRQ_HZ") / float(1000000))
            kk = 1000

            if Mhz >= float(821.5 - 2.5) and Mhz <= float(821.5 + 2.5):  # BANDWIDTH 5M 4G
                BANDWIDTH = 5 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(826.5 - 2.5) and Mhz <= float(826.5 + 2.5):  # BANDWIDTH 5M 2G
                BANDWIDTH = 5 * kk
                INFO2 = "SKT"
                INFO3 = "2G"
                Cate = 19
                THRESHOLD = 25
            elif Mhz >= float(834 - 5) and Mhz <= float(834 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(844 - 5) and Mhz <= float(844 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "LGU"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(866.5 - 2.5) and Mhz <= float(866.5 + 2.5):  # BANDWIDTH 5M 4G
                BANDWIDTH = 5 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(871.5 - 2.5) and Mhz <= float(871.5 + 2.5):  # BANDWIDTH 5M 2G
                BANDWIDTH = 5 * kk
                INFO2 = "SKT"
                INFO3 = "2G"
                Cate = 19
                THRESHOLD = 25
            elif Mhz >= float(879 - 5) and Mhz <= float(879 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(889 - 5) and Mhz <= float(889 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "LGU"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(909.3 - 5) and Mhz <= float(909.3 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(954.3 - 5) and Mhz <= float(954.3 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = -5
            elif Mhz >= float(1720 - 5) and Mhz <= float(1720 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 2
            elif Mhz >= float(1732.5 - 2.5) and Mhz <= float(1732.5 + 2.5):  # BANDWIDTH 5M 4G
                BANDWIDTH = 5 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 2
            elif Mhz >= float(1737.5 - 2.5) and Mhz <= float(1737.5 + 2.5):  # BANDWIDTH 5M 4G
                BANDWIDTH = 5 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 2
            elif Mhz >= float(1755 - 10) and Mhz <= float(1755 + 10):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 2
            elif Mhz >= float(1775 - 5) and Mhz <= float(1775 + 5):  # BANDWIDTH 10M 2G
                BANDWIDTH = 10 * kk
                INFO2 = "LGU"
                INFO3 = "2G"
                Cate = 19
                THRESHOLD = 32
            elif Mhz >= float(1820 - 10) and Mhz <= float(1820 + 10):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 2
            elif Mhz >= float(1845 - 16) and Mhz <= float(1845 + 16):  # BANDWIDTH 30M 4G
                BANDWIDTH = 30 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 2
            elif Mhz >= float(1865 - 5) and Mhz <= float(1865 + 5):  # BANDWIDTH 10M 2G
                BANDWIDTH = 10 * kk
                INFO2 = "LGU"
                INFO3 = "2G"
                Cate = 19
                THRESHOLD = 32
            elif Mhz >= float(1930 - 10) and Mhz <= float(1930 + 10):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "LGU"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 3
            elif Mhz >= float(1945 - 5) and Mhz <= float(1945 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 3
            elif Mhz >= float(1955 - 5) and Mhz <= float(1955 + 5):  # BANDWIDTH 10M 3G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "3G"
                Cate = 35
                THRESHOLD = 28
            elif Mhz >= float(1965 - 5) and Mhz <= float(1965 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 3
            elif Mhz >= float(1975 - 5) and Mhz <= float(1975 + 5):  # BANDWIDTH 10M 3G
                BANDWIDTH = 10 * kk
                INFO2 = "KT"
                INFO3 = "3G"
                Cate = 35
                THRESHOLD = 28
            elif Mhz >= float(2120 - 10) and Mhz <= float(2120 + 10):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "LGU"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 3
            elif Mhz >= float(2135 - 5) and Mhz <= float(2135 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 3
            elif Mhz >= float(2145 - 5) and Mhz <= float(2145 + 5):  # BANDWIDTH 10M 3G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "3G"
                Cate = 35
                THRESHOLD = 28
            elif Mhz >= float(2155 - 5) and Mhz <= float(2155 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "KT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 3
            elif Mhz >= float(2165 - 5) and Mhz <= float(2165 + 5):  # BANDWIDTH 10M 3G
                BANDWIDTH = 10 * kk
                INFO2 = "KT"
                INFO3 = "3G"
                Cate = 35
                THRESHOLD = 28
            elif Mhz >= float(2315 - 15) and Mhz <= float(2315 + 15):  # BANDWIDTH 30M WiBro 라서 INFO3 없음
                BANDWIDTH = 30 * kk
                INFO2 = "SKT"
                Cate = 40
            elif Mhz >= float(2345 - 15) and Mhz <= float(2345 + 15):  # BANDWIDTH 30M WiBro 라서 INFO3 없음
                BANDWIDTH = 30 * kk
                INFO2 = "KT"
                Cate = 40
            elif Mhz >= float(2510 - 10) and Mhz <= float(2510 + 10):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 5
            elif Mhz >= float(2530 - 10) and Mhz <= float(2530 + 10):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "LGU"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 5
            elif Mhz >= float(2545 - 5) and Mhz <= float(2545 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 5
            elif Mhz >= float(2630 - 5) and Mhz <= float(2630 + 5):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 5
            elif Mhz >= float(2650 - 5) and Mhz <= float(2650 + 5):  # BANDWIDTH 20M 4G
                BANDWIDTH = 20 * kk
                INFO2 = "LGU"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 5
            elif Mhz >= float(2665 - 5) and Mhz <= float(2665 + 5):  # BANDWIDTH 10M 4G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "4G"
                Cate = 60
                THRESHOLD = 5
            elif Mhz >= float(3460 - 40) and Mhz <= float(3460 + 40):  # BANDWIDTH 80M 5G
                BANDWIDTH = 80 * kk
                INFO2 = "LGU"
                INFO3 = "5G"
                Cate = 104
                THRESHOLD = -8
            elif Mhz >= float(3550 - 50) and Mhz <= float(3550 + 50):  # BANDWIDTH 50M #위랑 중복 발생 하지만, 실제로 사용되지 않음 5G
                BANDWIDTH = 50 * kk
                INFO2 = "SK"
                INFO3 = "5G"
                Cate = 104
                THRESHOLD = -8
            elif Mhz >= float(3650 - 50) and Mhz <= float(3650 + 50):  # BANDWIDTH 50M 5G
                BANDWIDTH = 10 * kk
                INFO2 = "SKT"
                INFO3 = "5G"
                Cate = 104
                THRESHOLD = -8
            elif Mhz >= float(26900 - 400) and Mhz <= float(26900 + 400):  # BANDWIDTH 800M 5G
                BANDWIDTH = 800 * kk
                INFO2 = "SK"
                INFO3 = "5G"
                Cate = 104
                THRESHOLD = 10
            elif Mhz >= float(27700 - 400) and Mhz <= float(27700 + 400):  # BANDWIDTH 800M 5G
                BANDWIDTH = 800 * kk
                INFO2 = "LGU"
                INFO3 = "5G"
                Cate = 104
                THRESHOLD = 10
            elif Mhz >= float(28500 - 400) and Mhz <= float(28500 + 400):  # BANDWIDTH 800M 5G
                BANDWIDTH = 800 * kk
                INFO2 = "SKT"
                INFO3 = "5G"
                Cate = 104
                THRESHOLD = 10
            else:
                BANDWIDTH = None
                Cate = None
                THRESHOLD = None
                INFO3 = None

        except:
            Mhz = None
            THRESHOLD = None

        ALTITUDE = str(list.get("ALTITUDE"))  # ALTITUDE 재정의
        if "None" in ALTITUDE:
            ALTITUDE = None

        NOMINAL_POWER = str(list.get("ARW_PWR_WTT"))  # ARW_PWR_WTT 재정의
        if "None" in NOMINAL_POWER:
            NOMINAL_POWER = None

        GAIN = str(list.get("ARW_GAN_NMV"))  # ARW_GAN_NMV 재정의
        if "None" in GAIN:
            GAIN = None
        GAINRX = GAIN

        LOSSES = str(list.get("LOSSES"))  # LOSSES 재정의
        if "None" in LOSSES:
            LOSSES = None

        LOSSESRX = str(list.get("LOSSESRX"))  # LOSSESRX 재정의
        if "None" in LOSSESRX:
            LOSSESRX = None

        H_ANTENNA = str(list.get("GND_ALTD_HET"))  # GND_ALTD_HET 재정의
        if "None" in H_ANTENNA:
            H_ANTENNA = None

        THRESHOLDRX = THRESHOLD
        # THRESHOLDRX = str(list.get("ThresholdRX")) # THRESHOLDRX 재정의
        # if "None" in THRESHOLDRX:
        #    THRESHOLDRX = None

        BANDWIDTHRX = BANDWIDTH
        # BANDWIDTHRX = str(list.get("BANDWIDTHRX")) # BANDWIDTHRX 재정의
        # if "None" in BANDWIDTH:
        #    BANDWIDTHRX = None

        if Cate == 60:  # 4G일때 pilot power
            Pilot = 5.556
        elif Cate == 35:  # 3G일때 pilot power
            Pilot = 10
        else:
            None

        INFO1 = str(list.get("RDS_PMS_NO"))
        CALL_SIGN = INFO1

        # INFO1 = str(list.get("SERVICE_NAME")) #SERVICE_NAME 크기가 길어서 25 이상이면 자르기
        if len(INFO1) >= 25:
            INFO1 = INFO1[:25]

        ADDRESS = str(list.get("RDS_TRS_ADR"))  # RDS_TRS_ADR 크기가 길어서 50 이상이면 자르기
        if len(ADDRESS) >= 50:
            ADDRESS = ADDRESS[:50]

        FKTB = -97  # 열잡음

        sql = "INSERT INTO " + j + "_" + i + " (CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE, NOMINAL_POWER, GAIN, GAINRX, LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, THRESHOLD, THRESHOLDRX, BANDWIDTH, BANDWIDTHRX, INFO1, INFO2, INFO3, Category, Pilot, FKTB) " \
                                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        val = [(CALL_SIGN, ADDRESS, '4DEC', str(list.get("LON")), str(list.get("LAT")),
                ALTITUDE, NOMINAL_POWER, GAIN, GAINRX, LOSSES, LOSSESRX, Mhz, H_ANTENNA,
                THRESHOLD, THRESHOLDRX, BANDWIDTH, BANDWIDTHRX, INFO1, INFO2, INFO3,
                Cate, Pilot, FKTB)]  # 쿼리를 통해 마리아 DB 데이터 입력

        cur.executemany(sql, val)
        conn.commit()

#
#  추가한 부분
#


SIGN = ['3G', '4G']
Agency = ['KT', 'SKT', 'LGU']
park_name = ['국립공원', '도립공원', '군립공원']

sql = "USE htzwarfare"
cur.execute(sql)  # 커서로 sql문 실행
for a in Agency:
    for b in SIGN:
        sql = "DROP TABLE IF EXISTS " + a + "_" + b
        cur.execute(sql)  # LGU_2g,3g,4g KT_3g,4g SKT_3g,4g 지우기(지우고 다시 생성하기 위해)

for a in Agency:
    for b in SIGN:
        sql = "DROP TABLE IF EXISTS " + a + "_" + b + "_lks"
        cur.execute(sql)  # LGU_2g,3g,4g KT_3g,4g SKT_3g,4g 지우기(지우고 다시 생성하기 위해)

sql = "DROP TABLE IF EXISTS LGU_2G"  # LGU_2G 는 따로 Drop
cur.execute(sql)  # 커서로 sql문 실행

sql = "DROP TABLE IF EXISTS LGU_2G_lks"  # LGU_2G_LKS 는 따로 Drop
cur.execute(sql)

for a in park_name:
    sql = "DROP TABLE IF EXISTS " + a
    cur.execute(sql)  # 국립공원, 군립공원 도립공원 지우기(지우고 다시 생성하기 위해)

for a in park_name:
    sql = "DROP TABLE IF EXISTS " + a + "_lks"
    cur.execute(sql)  # 국립공원, 군립공원 도립공원 지우기(지우고 다시 생성하기 위해)

sql = "CREATE TABLE IF NOT EXISTS LGU_2G (ID int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY," \
      "`CALL_SIGN` varchar(15) DEFAULT NULL," \
      "`ADDRESS` varchar(50) DEFAULT NULL," \
      "`NETID` varchar(25) DEFAULT NULL," \
      "`TYPE_COORD` varchar(10) DEFAULT NULL," \
      "`COORD_X` double DEFAULT NULL," \
      "`COORD_Y` double DEFAULT NULL," \
      "`ALTITUDE` smallint(6) DEFAULT NULL," \
      "`NOMINAL_POWER` double DEFAULT NULL," \
      "`GAIN` double DEFAULT NULL," \
      "`GAINRX` double DEFAULT NULL," \
      "`LOSSES` double DEFAULT NULL," \
      "`LOSSESRX` double DEFAULT NULL," \
      "`FREQUENCY` double DEFAULT NULL," \
      "`H_ANTENNA` double DEFAULT NULL," \
      "`POLAR` varchar(1) DEFAULT NULL," \
      "`POLARRX` varchar(1) DEFAULT NULL," \
      "`THRESHOLD` double DEFAULT NULL," \
      "`THRESHOLDRX` double DEFAULT NULL," \
      "`BANDWIDTH` double DEFAULT NULL," \
      "`BANDWIDTHRX` double DEFAULT NULL," \
      "`CHANNEL` smallint(6) DEFAULT NULL," \
      "`NB_LINES` smallint(6) DEFAULT NULL," \
      "`TITLE` varchar(25) DEFAULT NULL," \
      "`INFO1` varchar(25) DEFAULT NULL," \
      "`INFO2` varchar(25) DEFAULT NULL," \
      "`AZIMUTH` double DEFAULT NULL," \
      "`TILT` double DEFAULT NULL," \
      "`TILTE` double DEFAULT NULL," \
      "`TYPE_ELEMENT` smallint(6) DEFAULT NULL," \
      "`TYPE_STATION` varchar(1) DEFAULT NULL," \
      "`TYPE_LINK` varchar(2) DEFAULT NULL," \
      "`GROUP` varchar(3) DEFAULT NULL," \
      "`DIAG_H` varchar(288) DEFAULT NULL," \
      "`DIAG_V` varchar(716) DEFAULT NULL," \
      "`PROJECT_NAME` varchar(50) DEFAULT NULL," \
      "`Downlink_cx` int(11) DEFAULT NULL," \
      "`Uplink_cx` int(11) DEFAULT NULL," \
      "`D_cx1` double DEFAULT NULL," \
      "`U_cx1` double DEFAULT NULL," \
      "`D_cx2` double DEFAULT NULL," \
      "`U_cx2` double DEFAULT NULL," \
      "`D_cx3` double DEFAULT NULL," \
      "`U_cx3` double DEFAULT NULL," \
      "`D_cx4` double DEFAULT NULL," \
      "`U_cx4` double DEFAULT NULL," \
      "`D_cx5` double DEFAULT NULL," \
      "`U_cx5` double DEFAULT NULL," \
      "`D_cx6` double DEFAULT NULL," \
      "`U_cx6` double DEFAULT NULL," \
      "`D_cx7` double DEFAULT NULL," \
      "`U_cx7` double DEFAULT NULL," \
      "`D_cx8` double DEFAULT NULL," \
      "`U_cx8` double DEFAULT NULL," \
      "`D_cx9` double DEFAULT NULL," \
      "`U_cx9` double DEFAULT NULL," \
      "`D_cx10` double DEFAULT NULL," \
      "`U_cx10` double DEFAULT NULL," \
      "`D_cx11` double DEFAULT NULL," \
      "`U_cx11` double DEFAULT NULL," \
      "`D_cx12` double DEFAULT NULL," \
      "`U_cx12` double DEFAULT NULL," \
      "`D_cx13` double DEFAULT NULL," \
      "`U_cx13` double DEFAULT NULL," \
      "`D_cx14` double DEFAULT NULL," \
      "`U_cx14` double DEFAULT NULL," \
      "`D_cx15` double DEFAULT NULL," \
      "`U_cx15` double DEFAULT NULL," \
      "`D_cx16` double DEFAULT NULL," \
      "`U_cx16` double DEFAULT NULL," \
      "`Spacing` double DEFAULT NULL," \
      "`Category` int(11) DEFAULT NULL," \
      "`CodeSiteA` varchar(9) DEFAULT NULL," \
      "`WiencodeH` varchar(10) DEFAULT NULL," \
      "`WiencodeV` varchar(10) DEFAULT NULL," \
      "`Erlang` double DEFAULT NULL," \
      "`Call_no` double DEFAULT NULL," \
      "`Delay` smallint(6) DEFAULT NULL," \
      "`User` varchar(25) DEFAULT NULL," \
      "`RPE` varchar(50) DEFAULT NULL," \
      "`nfdname` varchar(21) DEFAULT NULL," \
      "`Antenna_nameH` varchar(25) DEFAULT NULL," \
      "`Antenna_nameV` varchar(25) DEFAULT NULL," \
      "`DateServ` double DEFAULT NULL," \
      "`DateBegin` double DEFAULT NULL," \
      "`DateEnd` double DEFAULT NULL," \
      "`LineOffset` smallint(6) DEFAULT NULL," \
      "`Precision` smallint(6) DEFAULT NULL," \
      "`Aperture` float DEFAULT NULL," \
      "`TIL` smallint(6) DEFAULT NULL," \
      "`Modulation` int(11) DEFAULT NULL," \
      "`FKTB` smallint(6) DEFAULT NULL," \
      "`Radius` float DEFAULT NULL," \
      "`THR10_3` float DEFAULT NULL," \
      "`THR10_6` float DEFAULT NULL," \
      "`THR10_8` float DEFAULT NULL," \
      "`THR10_10` float DEFAULT NULL," \
      "`Bit_rate` float DEFAULT NULL," \
      "`Channel_d` varchar(4) DEFAULT NULL," \
      "`Plan` varchar(10) DEFAULT NULL," \
      "`ICS_VALUE` longblob DEFAULT NULL," \
      "`HEFF_VI` varchar(180) DEFAULT NULL," \
      "`HEFF_GE` varchar(180) DEFAULT NULL," \
      "`ICST_STATUS` tinyint(4) DEFAULT NULL," \
      "`POLYGON` varchar(2000) DEFAULT NULL," \
      "`ANT_FILE` varchar(127) DEFAULT NULL," \
      "`Peak_Pow` double DEFAULT NULL," \
      "`OPTIONS` varchar(128) DEFAULT NULL," \
      "`Neighbours` varchar(512) DEFAULT NULL," \
      "`STATION_ID` int(11) DEFAULT NULL," \
      "`Color` int(11) DEFAULT NULL," \
      "`STRINGC` varchar(255) DEFAULT NULL," \
      "`TACLAC` int(11) DEFAULT NULL," \
      "`RSI` varchar(255) DEFAULT NULL," \
      "`MME` varchar(15) DEFAULT NULL," \
      "`SAEGW` varchar(15) DEFAULT NULL," \
      "`PATHCFD` varchar(255) DEFAULT NULL," \
      "`CI_N0` double DEFAULT NULL," \
      "`CI_N1` double DEFAULT NULL," \
      "`RDSPI_SID` int(11) DEFAULT NULL," \
      "`LSN_SWTPI` int(11) DEFAULT NULL," \
      "`TIImain` int(11) DEFAULT NULL," \
      "`TIIsub` int(11) DEFAULT NULL," \
      "`addloss` float DEFAULT NULL," \
      "`PNCODE` int(11) DEFAULT NULL," \
      "`FFFH_TRX` int(11) DEFAULT NULL," \
      "`SPURIOUS` int(11) DEFAULT NULL," \
      "`ETSI_CLASS` varchar(5) DEFAULT NULL," \
      "`SMART` int(11) DEFAULT NULL," \
      "`ARRAYTX` int(11) DEFAULT NULL," \
      "`ARRAYRX` int(11) DEFAULT NULL," \
      "`MU` int(11) DEFAULT NULL," \
      "`ADDPROPLOSSTX` int(11) DEFAULT NULL," \
      "`ADDPROPLOSSRX` int(11) DEFAULT NULL," \
      "`MEAN_FS_MS` float DEFAULT NULL," \
      "`MEAN_FS_MU` float DEFAULT NULL," \
      "`SIGMA_SS` float DEFAULT NULL," \
      "`SIGMA_SU` float DEFAULT NULL," \
      "`Pilot` float DEFAULT NULL," \
      "`Paging` float DEFAULT NULL," \
      "`Sync` float DEFAULT NULL," \
      "`Mchips_s` float DEFAULT NULL," \
      "`PDCCH` float DEFAULT NULL," \
      "`PBCH` float DEFAULT NULL," \
      "`PSS` float DEFAULT NULL," \
      "`SSS` float DEFAULT NULL," \
      "`PowerMaxW` double DEFAULT NULL," \
      "`CHANGE_DATE` double DEFAULT NULL," \
      "`XPD` int(11) DEFAULT NULL," \
      "`SectorBegin` int(11) DEFAULT NULL," \
      "`SectorEnd` int(11) DEFAULT NULL," \
      "`DistSimul` double DEFAULT NULL," \
      "`Pulse` float DEFAULT NULL," \
      "`Rd_Noise` float DEFAULT NULL," \
      "`Det_PD` float DEFAULT NULL," \
      "`Rd_PulseComp` smallint(6) DEFAULT NULL," \
      "`STRING` varchar(255) DEFAULT NULL," \
      "`CHG_DATE` double DEFAULT NULL," \
      "`TLEsatID` float DEFAULT NULL," \
      "`BEAMFORMINGH` int(11) DEFAULT NULL," \
      "`BEAMSTEPH` int(11) DEFAULT NULL," \
      "`BEAMSTEPV` int(11) DEFAULT NULL," \
      "`Numerology` int(11) DEFAULT NULL," \
      "`BEAMFORMINGV` int(11) DEFAULT NULL," \
      "`LAYERS` int(11) DEFAULT NULL," \
      "`RS_Boost` smallint(6) DEFAULT NULL," \
      "`DL_UL` float DEFAULT NULL," \
      "`Activity` smallint(6) DEFAULT NULL," \
      "`STATUS_ELEMENT` smallint(6) DEFAULT NULL," \
      "`RNPC` smallint(6) DEFAULT NULL," \
      "KEY `ID` (`ID`) USING BTREE" \
      ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"
cur.execute(sql)

sql = "CREATE TABLE IF NOT EXISTS LGU_2G_lks (" \
      "`ID` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT," \
      "`CS_TX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
      "`CS_RX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
      "`LINKNAME` VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
      "`BITRATE` DOUBLE NULL DEFAULT NULL," \
      "`HANDOVER_MARGIN` INT(11) NULL DEFAULT NULL," \
      "INDEX `ID` (`ID`) USING BTREE" \
      ") COLLATE='utf16_general_ci' ENGINE=InnoDB;"
cur.execute(sql)

for a in park_name:  # 국립공원, 도립공원, 군립공원 테이블 생성
    sql = "CREATE TABLE IF NOT EXISTS " + a + " (ID int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY," \
                                              "`CALL_SIGN` varchar(15) DEFAULT NULL," \
                                              "`ADDRESS` varchar(50) DEFAULT NULL," \
                                              "`NETID` varchar(25) DEFAULT NULL," \
                                              "`TYPE_COORD` varchar(10) DEFAULT NULL," \
                                              "`COORD_X` double DEFAULT NULL," \
                                              "`COORD_Y` double DEFAULT NULL," \
                                              "`ALTITUDE` smallint(6) DEFAULT NULL," \
                                              "`NOMINAL_POWER` double DEFAULT NULL," \
                                              "`GAIN` double DEFAULT NULL," \
                                              "`GAINRX` double DEFAULT NULL," \
                                              "`LOSSES` double DEFAULT NULL," \
                                              "`LOSSESRX` double DEFAULT NULL," \
                                              "`FREQUENCY` double DEFAULT NULL," \
                                              "`H_ANTENNA` double DEFAULT NULL," \
                                              "`POLAR` varchar(1) DEFAULT NULL," \
                                              "`POLARRX` varchar(1) DEFAULT NULL," \
                                              "`THRESHOLD` double DEFAULT NULL," \
                                              "`THRESHOLDRX` double DEFAULT NULL," \
                                              "`BANDWIDTH` double DEFAULT NULL," \
                                              "`BANDWIDTHRX` double DEFAULT NULL," \
                                              "`CHANNEL` smallint(6) DEFAULT NULL," \
                                              "`NB_LINES` smallint(6) DEFAULT NULL," \
                                              "`TITLE` varchar(25) DEFAULT NULL," \
                                              "`INFO1` varchar(25) DEFAULT NULL," \
                                              "`INFO2` varchar(25) DEFAULT NULL," \
                                              "`AZIMUTH` double DEFAULT NULL," \
                                              "`TILT` double DEFAULT NULL," \
                                              "`TILTE` double DEFAULT NULL," \
                                              "`TYPE_ELEMENT` smallint(6) DEFAULT NULL," \
                                              "`TYPE_STATION` varchar(1) DEFAULT NULL," \
                                              "`TYPE_LINK` varchar(2) DEFAULT NULL," \
                                              "`GROUP` varchar(3) DEFAULT NULL," \
                                              "`DIAG_H` varchar(288) DEFAULT NULL," \
                                              "`DIAG_V` varchar(716) DEFAULT NULL," \
                                              "`PROJECT_NAME` varchar(50) DEFAULT NULL," \
                                              "`Downlink_cx` int(11) DEFAULT NULL," \
                                              "`Uplink_cx` int(11) DEFAULT NULL," \
                                              "`D_cx1` double DEFAULT NULL," \
                                              "`U_cx1` double DEFAULT NULL," \
                                              "`D_cx2` double DEFAULT NULL," \
                                              "`U_cx2` double DEFAULT NULL," \
                                              "`D_cx3` double DEFAULT NULL," \
                                              "`U_cx3` double DEFAULT NULL," \
                                              "`D_cx4` double DEFAULT NULL," \
                                              "`U_cx4` double DEFAULT NULL," \
                                              "`D_cx5` double DEFAULT NULL," \
                                              "`U_cx5` double DEFAULT NULL," \
                                              "`D_cx6` double DEFAULT NULL," \
                                              "`U_cx6` double DEFAULT NULL," \
                                              "`D_cx7` double DEFAULT NULL," \
                                              "`U_cx7` double DEFAULT NULL," \
                                              "`D_cx8` double DEFAULT NULL," \
                                              "`U_cx8` double DEFAULT NULL," \
                                              "`D_cx9` double DEFAULT NULL," \
                                              "`U_cx9` double DEFAULT NULL," \
                                              "`D_cx10` double DEFAULT NULL," \
                                              "`U_cx10` double DEFAULT NULL," \
                                              "`D_cx11` double DEFAULT NULL," \
                                              "`U_cx11` double DEFAULT NULL," \
                                              "`D_cx12` double DEFAULT NULL," \
                                              "`U_cx12` double DEFAULT NULL," \
                                              "`D_cx13` double DEFAULT NULL," \
                                              "`U_cx13` double DEFAULT NULL," \
                                              "`D_cx14` double DEFAULT NULL," \
                                              "`U_cx14` double DEFAULT NULL," \
                                              "`D_cx15` double DEFAULT NULL," \
                                              "`U_cx15` double DEFAULT NULL," \
                                              "`D_cx16` double DEFAULT NULL," \
                                              "`U_cx16` double DEFAULT NULL," \
                                              "`Spacing` double DEFAULT NULL," \
                                              "`Category` int(11) DEFAULT NULL," \
                                              "`CodeSiteA` varchar(9) DEFAULT NULL," \
                                              "`WiencodeH` varchar(10) DEFAULT NULL," \
                                              "`WiencodeV` varchar(10) DEFAULT NULL," \
                                              "`Erlang` double DEFAULT NULL," \
                                              "`Call_no` double DEFAULT NULL," \
                                              "`Delay` smallint(6) DEFAULT NULL," \
                                              "`User` varchar(25) DEFAULT NULL," \
                                              "`RPE` varchar(50) DEFAULT NULL," \
                                              "`nfdname` varchar(21) DEFAULT NULL," \
                                              "`Antenna_nameH` varchar(25) DEFAULT NULL," \
                                              "`Antenna_nameV` varchar(25) DEFAULT NULL," \
                                              "`DateServ` double DEFAULT NULL," \
                                              "`DateBegin` double DEFAULT NULL," \
                                              "`DateEnd` double DEFAULT NULL," \
                                              "`LineOffset` smallint(6) DEFAULT NULL," \
                                              "`Precision` smallint(6) DEFAULT NULL," \
                                              "`Aperture` float DEFAULT NULL," \
                                              "`TIL` smallint(6) DEFAULT NULL," \
                                              "`Modulation` int(11) DEFAULT NULL," \
                                              "`FKTB` smallint(6) DEFAULT NULL," \
                                              "`Radius` float DEFAULT NULL," \
                                              "`THR10_3` float DEFAULT NULL," \
                                              "`THR10_6` float DEFAULT NULL," \
                                              "`THR10_8` float DEFAULT NULL," \
                                              "`THR10_10` float DEFAULT NULL," \
                                              "`Bit_rate` float DEFAULT NULL," \
                                              "`Channel_d` varchar(4) DEFAULT NULL," \
                                              "`Plan` varchar(10) DEFAULT NULL," \
                                              "`ICS_VALUE` longblob DEFAULT NULL," \
                                              "`HEFF_VI` varchar(180) DEFAULT NULL," \
                                              "`HEFF_GE` varchar(180) DEFAULT NULL," \
                                              "`ICST_STATUS` tinyint(4) DEFAULT NULL," \
                                              "`POLYGON` varchar(2000) DEFAULT NULL," \
                                              "`ANT_FILE` varchar(127) DEFAULT NULL," \
                                              "`Peak_Pow` double DEFAULT NULL," \
                                              "`OPTIONS` varchar(128) DEFAULT NULL," \
                                              "`Neighbours` varchar(512) DEFAULT NULL," \
                                              "`STATION_ID` int(11) DEFAULT NULL," \
                                              "`Color` int(11) DEFAULT NULL," \
                                              "`STRINGC` varchar(255) DEFAULT NULL," \
                                              "`TACLAC` int(11) DEFAULT NULL," \
                                              "`RSI` varchar(255) DEFAULT NULL," \
                                              "`MME` varchar(15) DEFAULT NULL," \
                                              "`SAEGW` varchar(15) DEFAULT NULL," \
                                              "`PATHCFD` varchar(255) DEFAULT NULL," \
                                              "`CI_N0` double DEFAULT NULL," \
                                              "`CI_N1` double DEFAULT NULL," \
                                              "`RDSPI_SID` int(11) DEFAULT NULL," \
                                              "`LSN_SWTPI` int(11) DEFAULT NULL," \
                                              "`TIImain` int(11) DEFAULT NULL," \
                                              "`TIIsub` int(11) DEFAULT NULL," \
                                              "`addloss` float DEFAULT NULL," \
                                              "`PNCODE` int(11) DEFAULT NULL," \
                                              "`FFFH_TRX` int(11) DEFAULT NULL," \
                                              "`SPURIOUS` int(11) DEFAULT NULL," \
                                              "`ETSI_CLASS` varchar(5) DEFAULT NULL," \
                                              "`SMART` int(11) DEFAULT NULL," \
                                              "`ARRAYTX` int(11) DEFAULT NULL," \
                                              "`ARRAYRX` int(11) DEFAULT NULL," \
                                              "`MU` int(11) DEFAULT NULL," \
                                              "`ADDPROPLOSSTX` int(11) DEFAULT NULL," \
                                              "`ADDPROPLOSSRX` int(11) DEFAULT NULL," \
                                              "`MEAN_FS_MS` float DEFAULT NULL," \
                                              "`MEAN_FS_MU` float DEFAULT NULL," \
                                              "`SIGMA_SS` float DEFAULT NULL," \
                                              "`SIGMA_SU` float DEFAULT NULL," \
                                              "`Pilot` float DEFAULT NULL," \
                                              "`Paging` float DEFAULT NULL," \
                                              "`Sync` float DEFAULT NULL," \
                                              "`Mchips_s` float DEFAULT NULL," \
                                              "`PDCCH` float DEFAULT NULL," \
                                              "`PBCH` float DEFAULT NULL," \
                                              "`PSS` float DEFAULT NULL," \
                                              "`SSS` float DEFAULT NULL," \
                                              "`PowerMaxW` double DEFAULT NULL," \
                                              "`CHANGE_DATE` double DEFAULT NULL," \
                                              "`XPD` int(11) DEFAULT NULL," \
                                              "`SectorBegin` int(11) DEFAULT NULL," \
                                              "`SectorEnd` int(11) DEFAULT NULL," \
                                              "`DistSimul` double DEFAULT NULL," \
                                              "`Pulse` float DEFAULT NULL," \
                                              "`Rd_Noise` float DEFAULT NULL," \
                                              "`Det_PD` float DEFAULT NULL," \
                                              "`Rd_PulseComp` smallint(6) DEFAULT NULL," \
                                              "`STRING` varchar(255) DEFAULT NULL," \
                                              "`CHG_DATE` double DEFAULT NULL," \
                                              "`TLEsatID` float DEFAULT NULL," \
                                              "`BEAMFORMINGH` int(11) DEFAULT NULL," \
                                              "`BEAMSTEPH` int(11) DEFAULT NULL," \
                                              "`BEAMSTEPV` int(11) DEFAULT NULL," \
                                              "`Numerology` int(11) DEFAULT NULL," \
                                              "`BEAMFORMINGV` int(11) DEFAULT NULL," \
                                              "`LAYERS` int(11) DEFAULT NULL," \
                                              "`RS_Boost` smallint(6) DEFAULT NULL," \
                                              "`DL_UL` float DEFAULT NULL," \
                                              "`Activity` smallint(6) DEFAULT NULL," \
                                              "`STATUS_ELEMENT` smallint(6) DEFAULT NULL," \
                                              "`RNPC` smallint(6) DEFAULT NULL," \
                                              "KEY `ID` (`ID`) USING BTREE" \
                                              ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"
    cur.execute(sql)

for a in park_name:
    sql = "CREATE TABLE IF NOT EXISTS " + a + "_lks (" \
                                              "`ID` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT," \
                                              "`CS_TX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                                              "`CS_RX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                                              "`LINKNAME` VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                                              "`BITRATE` DOUBLE NULL DEFAULT NULL," \
                                              "`HANDOVER_MARGIN` INT(11) NULL DEFAULT NULL," \
                                              "INDEX `ID` (`ID`) USING BTREE" \
                                              ") COLLATE='utf16_general_ci' ENGINE=InnoDB;"
    cur.execute(sql)  # 국립공원, 군립공원 도립공원_lks 생성

for a in Agency:  # LGU_2g,3g,4g KT_3g,4g SKT_3g,4g 생성
    for b in SIGN:
        sql = "CREATE TABLE IF NOT EXISTS " + a + "_" + b + " (ID int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY," \
                                                            "`CALL_SIGN` varchar(15) DEFAULT NULL," \
                                                            "`ADDRESS` varchar(50) DEFAULT NULL," \
                                                            "`NETID` varchar(25) DEFAULT NULL," \
                                                            "`TYPE_COORD` varchar(10) DEFAULT NULL," \
                                                            "`COORD_X` double DEFAULT NULL," \
                                                            "`COORD_Y` double DEFAULT NULL," \
                                                            "`ALTITUDE` smallint(6) DEFAULT NULL," \
                                                            "`NOMINAL_POWER` double DEFAULT NULL," \
                                                            "`GAIN` double DEFAULT NULL," \
                                                            "`GAINRX` double DEFAULT NULL," \
                                                            "`LOSSES` double DEFAULT NULL," \
                                                            "`LOSSESRX` double DEFAULT NULL," \
                                                            "`FREQUENCY` double DEFAULT NULL," \
                                                            "`H_ANTENNA` double DEFAULT NULL," \
                                                            "`POLAR` varchar(1) DEFAULT NULL," \
                                                            "`POLARRX` varchar(1) DEFAULT NULL," \
                                                            "`THRESHOLD` double DEFAULT NULL," \
                                                            "`THRESHOLDRX` double DEFAULT NULL," \
                                                            "`BANDWIDTH` double DEFAULT NULL," \
                                                            "`BANDWIDTHRX` double DEFAULT NULL," \
                                                            "`CHANNEL` smallint(6) DEFAULT NULL," \
                                                            "`NB_LINES` smallint(6) DEFAULT NULL," \
                                                            "`TITLE` varchar(25) DEFAULT NULL," \
                                                            "`INFO1` varchar(25) DEFAULT NULL," \
                                                            "`INFO2` varchar(25) DEFAULT NULL," \
                                                            "`AZIMUTH` double DEFAULT NULL," \
                                                            "`TILT` double DEFAULT NULL," \
                                                            "`TILTE` double DEFAULT NULL," \
                                                            "`TYPE_ELEMENT` smallint(6) DEFAULT NULL," \
                                                            "`TYPE_STATION` varchar(1) DEFAULT NULL," \
                                                            "`TYPE_LINK` varchar(2) DEFAULT NULL," \
                                                            "`GROUP` varchar(3) DEFAULT NULL," \
                                                            "`DIAG_H` varchar(288) DEFAULT NULL," \
                                                            "`DIAG_V` varchar(716) DEFAULT NULL," \
                                                            "`PROJECT_NAME` varchar(50) DEFAULT NULL," \
                                                            "`Downlink_cx` int(11) DEFAULT NULL," \
                                                            "`Uplink_cx` int(11) DEFAULT NULL," \
                                                            "`D_cx1` double DEFAULT NULL," \
                                                            "`U_cx1` double DEFAULT NULL," \
                                                            "`D_cx2` double DEFAULT NULL," \
                                                            "`U_cx2` double DEFAULT NULL," \
                                                            "`D_cx3` double DEFAULT NULL," \
                                                            "`U_cx3` double DEFAULT NULL," \
                                                            "`D_cx4` double DEFAULT NULL," \
                                                            "`U_cx4` double DEFAULT NULL," \
                                                            "`D_cx5` double DEFAULT NULL," \
                                                            "`U_cx5` double DEFAULT NULL," \
                                                            "`D_cx6` double DEFAULT NULL," \
                                                            "`U_cx6` double DEFAULT NULL," \
                                                            "`D_cx7` double DEFAULT NULL," \
                                                            "`U_cx7` double DEFAULT NULL," \
                                                            "`D_cx8` double DEFAULT NULL," \
                                                            "`U_cx8` double DEFAULT NULL," \
                                                            "`D_cx9` double DEFAULT NULL," \
                                                            "`U_cx9` double DEFAULT NULL," \
                                                            "`D_cx10` double DEFAULT NULL," \
                                                            "`U_cx10` double DEFAULT NULL," \
                                                            "`D_cx11` double DEFAULT NULL," \
                                                            "`U_cx11` double DEFAULT NULL," \
                                                            "`D_cx12` double DEFAULT NULL," \
                                                            "`U_cx12` double DEFAULT NULL," \
                                                            "`D_cx13` double DEFAULT NULL," \
                                                            "`U_cx13` double DEFAULT NULL," \
                                                            "`D_cx14` double DEFAULT NULL," \
                                                            "`U_cx14` double DEFAULT NULL," \
                                                            "`D_cx15` double DEFAULT NULL," \
                                                            "`U_cx15` double DEFAULT NULL," \
                                                            "`D_cx16` double DEFAULT NULL," \
                                                            "`U_cx16` double DEFAULT NULL," \
                                                            "`Spacing` double DEFAULT NULL," \
                                                            "`Category` int(11) DEFAULT NULL," \
                                                            "`CodeSiteA` varchar(9) DEFAULT NULL," \
                                                            "`WiencodeH` varchar(10) DEFAULT NULL," \
                                                            "`WiencodeV` varchar(10) DEFAULT NULL," \
                                                            "`Erlang` double DEFAULT NULL," \
                                                            "`Call_no` double DEFAULT NULL," \
                                                            "`Delay` smallint(6) DEFAULT NULL," \
                                                            "`User` varchar(25) DEFAULT NULL," \
                                                            "`RPE` varchar(50) DEFAULT NULL," \
                                                            "`nfdname` varchar(21) DEFAULT NULL," \
                                                            "`Antenna_nameH` varchar(25) DEFAULT NULL," \
                                                            "`Antenna_nameV` varchar(25) DEFAULT NULL," \
                                                            "`DateServ` double DEFAULT NULL," \
                                                            "`DateBegin` double DEFAULT NULL," \
                                                            "`DateEnd` double DEFAULT NULL," \
                                                            "`LineOffset` smallint(6) DEFAULT NULL," \
                                                            "`Precision` smallint(6) DEFAULT NULL," \
                                                            "`Aperture` float DEFAULT NULL," \
                                                            "`TIL` smallint(6) DEFAULT NULL," \
                                                            "`Modulation` int(11) DEFAULT NULL," \
                                                            "`FKTB` smallint(6) DEFAULT NULL," \
                                                            "`Radius` float DEFAULT NULL," \
                                                            "`THR10_3` float DEFAULT NULL," \
                                                            "`THR10_6` float DEFAULT NULL," \
                                                            "`THR10_8` float DEFAULT NULL," \
                                                            "`THR10_10` float DEFAULT NULL," \
                                                            "`Bit_rate` float DEFAULT NULL," \
                                                            "`Channel_d` varchar(4) DEFAULT NULL," \
                                                            "`Plan` varchar(10) DEFAULT NULL," \
                                                            "`ICS_VALUE` longblob DEFAULT NULL," \
                                                            "`HEFF_VI` varchar(180) DEFAULT NULL," \
                                                            "`HEFF_GE` varchar(180) DEFAULT NULL," \
                                                            "`ICST_STATUS` tinyint(4) DEFAULT NULL," \
                                                            "`POLYGON` varchar(2000) DEFAULT NULL," \
                                                            "`ANT_FILE` varchar(127) DEFAULT NULL," \
                                                            "`Peak_Pow` double DEFAULT NULL," \
                                                            "`OPTIONS` varchar(128) DEFAULT NULL," \
                                                            "`Neighbours` varchar(512) DEFAULT NULL," \
                                                            "`STATION_ID` int(11) DEFAULT NULL," \
                                                            "`Color` int(11) DEFAULT NULL," \
                                                            "`STRINGC` varchar(255) DEFAULT NULL," \
                                                            "`TACLAC` int(11) DEFAULT NULL," \
                                                            "`RSI` varchar(255) DEFAULT NULL," \
                                                            "`MME` varchar(15) DEFAULT NULL," \
                                                            "`SAEGW` varchar(15) DEFAULT NULL," \
                                                            "`PATHCFD` varchar(255) DEFAULT NULL," \
                                                            "`CI_N0` double DEFAULT NULL," \
                                                            "`CI_N1` double DEFAULT NULL," \
                                                            "`RDSPI_SID` int(11) DEFAULT NULL," \
                                                            "`LSN_SWTPI` int(11) DEFAULT NULL," \
                                                            "`TIImain` int(11) DEFAULT NULL," \
                                                            "`TIIsub` int(11) DEFAULT NULL," \
                                                            "`addloss` float DEFAULT NULL," \
                                                            "`PNCODE` int(11) DEFAULT NULL," \
                                                            "`FFFH_TRX` int(11) DEFAULT NULL," \
                                                            "`SPURIOUS` int(11) DEFAULT NULL," \
                                                            "`ETSI_CLASS` varchar(5) DEFAULT NULL," \
                                                            "`SMART` int(11) DEFAULT NULL," \
                                                            "`ARRAYTX` int(11) DEFAULT NULL," \
                                                            "`ARRAYRX` int(11) DEFAULT NULL," \
                                                            "`MU` int(11) DEFAULT NULL," \
                                                            "`ADDPROPLOSSTX` int(11) DEFAULT NULL," \
                                                            "`ADDPROPLOSSRX` int(11) DEFAULT NULL," \
                                                            "`MEAN_FS_MS` float DEFAULT NULL," \
                                                            "`MEAN_FS_MU` float DEFAULT NULL," \
                                                            "`SIGMA_SS` float DEFAULT NULL," \
                                                            "`SIGMA_SU` float DEFAULT NULL," \
                                                            "`Pilot` float DEFAULT NULL," \
                                                            "`Paging` float DEFAULT NULL," \
                                                            "`Sync` float DEFAULT NULL," \
                                                            "`Mchips_s` float DEFAULT NULL," \
                                                            "`PDCCH` float DEFAULT NULL," \
                                                            "`PBCH` float DEFAULT NULL," \
                                                            "`PSS` float DEFAULT NULL," \
                                                            "`SSS` float DEFAULT NULL," \
                                                            "`PowerMaxW` double DEFAULT NULL," \
                                                            "`CHANGE_DATE` double DEFAULT NULL," \
                                                            "`XPD` int(11) DEFAULT NULL," \
                                                            "`SectorBegin` int(11) DEFAULT NULL," \
                                                            "`SectorEnd` int(11) DEFAULT NULL," \
                                                            "`DistSimul` double DEFAULT NULL," \
                                                            "`Pulse` float DEFAULT NULL," \
                                                            "`Rd_Noise` float DEFAULT NULL," \
                                                            "`Det_PD` float DEFAULT NULL," \
                                                            "`Rd_PulseComp` smallint(6) DEFAULT NULL," \
                                                            "`STRING` varchar(255) DEFAULT NULL," \
                                                            "`CHG_DATE` double DEFAULT NULL," \
                                                            "`TLEsatID` float DEFAULT NULL," \
                                                            "`BEAMFORMINGH` int(11) DEFAULT NULL," \
                                                            "`BEAMSTEPH` int(11) DEFAULT NULL," \
                                                            "`BEAMSTEPV` int(11) DEFAULT NULL," \
                                                            "`Numerology` int(11) DEFAULT NULL," \
                                                            "`BEAMFORMINGV` int(11) DEFAULT NULL," \
                                                            "`LAYERS` int(11) DEFAULT NULL," \
                                                            "`RS_Boost` smallint(6) DEFAULT NULL," \
                                                            "`DL_UL` float DEFAULT NULL," \
                                                            "`Activity` smallint(6) DEFAULT NULL," \
                                                            "`STATUS_ELEMENT` smallint(6) DEFAULT NULL," \
                                                            "`RNPC` smallint(6) DEFAULT NULL," \
                                                            "KEY `ID` (`ID`) USING BTREE" \
                                                            ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"

        cur.execute(sql)

for a in Agency:
    for b in SIGN:
        sql = "CREATE TABLE IF NOT EXISTS " + a + "_" + b + "_lks (" \
                                                            "`ID` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT," \
                                                            "`CS_TX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                                                            "`CS_RX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                                                            "`LINKNAME` VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                                                            "`BITRATE` DOUBLE NULL DEFAULT NULL," \
                                                            "`HANDOVER_MARGIN` INT(11) NULL DEFAULT NULL," \
                                                            "INDEX `ID` (`ID`) USING BTREE" \
                                                            ") COLLATE='utf16_general_ci' ENGINE=InnoDB;"

        cur.execute(sql)  # LGU_2g,3g,4g KT_3g,4g SKT_3g,4g_lks 생성

sql = "USE " + DBname
cur.execute(sql)  # 커서로 sql문 실행

table_name = []
sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '" + DBname + "'"  # KCAdb 테이블 정보 가지고 오기
cur.execute(sql)

for temp in cur:  # 데이블 이름 맞게 조절 ex) 가야산_국립공원
    temp = str(temp)
    temp = temp[2:-3]
    table_name.append(temp)

for a in table_name:  # # LGU_2g,3g,4g KT_3g,4g SKT_3g,4g 에 데이터 삽입
    for b in Agency:
        for c in SIGN:
            sql = "INSERT INTO htzwarfare. " + b + "_" + c + \
                  "(CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE, NOMINAL_POWER, GAIN, GAINRX, " \
                  "LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, " \
                  "BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, INFO1, INFO2, Category, Pilot, FKTB) " \
                  "SELECT CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE," \
                  " NOMINAL_POWER, GAIN, GAINRX, LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, " \
                  "POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, " \
                  "CALL_SIGN, INFO2, Category ,Pilot, FKTB " \
                  "FROM " + a + \
                  " WHERE INFO2 = '" + b + "' AND INFO3 = '" + c + "'"
            cur.execute(sql)
            conn.commit()

for temp in table_name:  # 국립공원, 도립공원, 군립공원 테이블 추가 htzdb
    temp_name = temp[-4:]
    if temp_name == "군립공원":
        sql = "INSERT INTO htzwarfare.군립공원" \
              "(CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE, NOMINAL_POWER, GAIN, GAINRX, " \
              "LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, " \
              "BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, INFO1, INFO2, Category, Pilot, FKTB) " \
              "SELECT CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE," \
              " NOMINAL_POWER, GAIN, GAINRX, LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, " \
              "POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, " \
              "CALL_SIGN, INFO2, Category ,Pilot, FKTB " \
              "FROM " + temp

    elif temp_name == "도립공원":
        sql = "INSERT INTO htzwarfare.도립공원" \
              "(CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE, NOMINAL_POWER, GAIN, GAINRX, " \
              "LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, " \
              "BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, INFO1, INFO2, Category, Pilot, FKTB) " \
              "SELECT CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE," \
              " NOMINAL_POWER, GAIN, GAINRX, LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, " \
              "POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, " \
              "CALL_SIGN, INFO2, Category ,Pilot, FKTB " \
              "FROM " + temp
    elif temp_name == "국립공원":
        sql = "INSERT INTO htzwarfare.국립공원" \
              "(CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE, NOMINAL_POWER, GAIN, GAINRX, " \
              "LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, " \
              "BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, INFO1, INFO2, Category, Pilot, FKTB) " \
              "SELECT CALL_SIGN, ADDRESS, TYPE_COORD, COORD_X, COORD_Y, ALTITUDE," \
              " NOMINAL_POWER, GAIN, GAINRX, LOSSES, LOSSESRX, FREQUENCY, H_ANTENNA, POLAR, " \
              "POLARRX, THRESHOLD, THRESHOLDRX, BANDWIDTH, BANDWIDTHRX, CHANNEL, NB_LINES, TITLE, " \
              "CALL_SIGN, INFO2, Category ,Pilot, FKTB " \
              "FROM " + temp
    cur.execute(sql)
    conn.commit()

print("\nDB업데이트가 완료되었습니다.")

# bat 파일 실행 부분 GUI가 생성되면
# ex) kt-3g, kt-4g, kt-5g 이런식으로 각각의 버튼이 있고 그 버튼을 클릭하면 실행하게
# export.bat는 DB내용이 바뀌었을 때 실행하게 하기, (이유 : 실행하는데 오래 걸림, 그냥 bat 파일은 export의 결과라고 보면 됨)
#os.system(r'C:\auto_test\fileBatch\PROx\kt-3g.bat')

conn.close()


