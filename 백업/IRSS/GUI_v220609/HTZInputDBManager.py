from xmlrpc.client import Boolean
from numpy import true_divide
import pymysql

class HTZInputDBManager(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.host_address = ""
        self.port_num = 3307
        self.username = ""
        self.password = ""
        self.db_name = "irss_db"
        self.connect_called = False
        self.__alphabet_list = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n"]

        # 안테나 패턴명 기본값
        self.ant_name_non_dir_horizon = "1.SPH"
        self.ant_name_non_dir_vertical = "1.SPV"
        self.ant_name_directional_horizon = "14.SPH"
        self.ant_name_directional_vertical = "14.SPV"

        # 테이블 앞에 붙는 이름        
        self.table_name_prefix_update_required = "update_"      # 갱신 필요 기지국 목록 DB 이름 앞에 붙일 문자 (공백x)
        self.table_name_prefix_analysis_completed = ""          # 완료 DB 앞에 붙일 문자

        # 테이블에 Insert시 입력 column 목록 (모든 column의 목록은 아님)

        # 섹터가 없는 경우
        self.insert_query_column_list_single_azimuth = ["CALL_SIGN", "ADDRESS", "TYPE_COORD", "COORD_X", "COORD_Y", 
                                "ALTITUDE", "NOMINAL_POWER", "GAIN", "GAINRX", "LOSSES", 
                                "LOSSESRX", "FREQUENCY", "H_ANTENNA", "THRESHOLD", "THRESHOLDRX", 
                                "BANDWIDTH", "BANDWIDTHRX", "INFO1", "INFO2", "DateServ", 
                                "ICST_STATUS", "AZIMUTH", "INFO3", "Category", "Pilot", 
                                "FKTB", "RS_Boost", "TILT"]

        # 섹터가 있는 경우 : "Antenna_nameH", "Antenna_nameV", "WiencodeH", "WiencodeV" 추가됨
        self.insert_query_column_list_multiple_azimuth = ["CALL_SIGN", "ADDRESS", "TYPE_COORD", "COORD_X", "COORD_Y", 
                                "ALTITUDE", "NOMINAL_POWER", "GAIN", "GAINRX", "LOSSES", 
                                "LOSSESRX", "FREQUENCY", "H_ANTENNA", "THRESHOLD", "THRESHOLDRX", 
                                "BANDWIDTH", "BANDWIDTHRX", "INFO1", "INFO2", "DateServ", 
                                "ICST_STATUS", "AZIMUTH", "INFO3", "Category", "Pilot", 
                                "FKTB", "Antenna_nameH", "Antenna_nameV", "WiencodeH", "WiencodeV", 
                                "RS_Boost", "TILT"]

        # INSERT INTO [테이블] ([A]) VALUES ([B]) 쿼리문에 들어갈 문자열을 미리 구성

        # [A] 부분
        created_string = ""
        for idx, column_name in enumerate(self.insert_query_column_list_single_azimuth):
            if(idx == 0):
                created_string = created_string + column_name
            else:
                created_string = created_string + "," + column_name
        self.sql_column_string_single_azimuth = created_string

        created_string = ""
        for idx, column_name in enumerate(self.insert_query_column_list_multiple_azimuth):
            if(idx == 0):
                created_string = created_string + column_name
            else:
                created_string = created_string + "," + column_name
        self.sql_column_string_multiple_azimuth = created_string

        # [B] 부분의 형식 문자열 : "%s, %s, ... " 를 Value 갯수만큼 구성
        created_string = ""
        for idx in range(0, len(self.insert_query_column_list_single_azimuth)):
            if(idx == 0):
                created_string = created_string + "%s"
            else:
                created_string = created_string + ",%s"
        self.sql_values_input_string_single_azimuth = created_string

        created_string = ""
        for idx in range(0, len(self.insert_query_column_list_multiple_azimuth)):
            if(idx == 0):
                created_string = created_string + "%s"
            else:
                created_string = created_string + ",%s"
        self.sql_values_input_string_multiple_azimuth = created_string

        # 테이블 생성 쿼리 중 테이블 구조 부분 문자열
        # 괄호 안에 들어가는 문자열 처리하므로 괄호 뺄 것.

        # 테이블 내 Primary key 열 번호
        self.key_column_index_id = 0        # ID
        self.key_column_index_info1 = 24    # INFO1 : RDS_TRS_ADR + "_" + 번호(1, 2, 3, ...) --> 갱신 확인 용도
        self.column_index_ics_value = 101   # ICS_VALUE 열

        # 시나리오 별 테이블 생성 필요할 수 있어서 반복성 발생 가능 --> 코드 길이 최소화
        self.htz_link_tbl_create_query_str = "`ID` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT," \
                "`CS_TX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                "`CS_RX` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                "`LINKNAME` VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf16_general_ci'," \
                "`BITRATE` DOUBLE NULL DEFAULT NULL,"\
                "`HANDOVER_MARGIN` INT(11) NULL DEFAULT NULL,"\
                "INDEX `ID` (`ID`) USING BTREE"

        self.common_sql_query_str = "ID int(10) DEFAULT NULL," \
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
                    "`INFO1` varchar(25) NOT NULL UNIQUE," \
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
                    "PRIMARY KEY `INFO1` (`INFO1`) USING BTREE" \

        # KCA 주파수 맵핑 CSV 파일 읽어서 채우기
        self.__kca_freq_table = []
        try:
            with open("kca_freq_table.csv", "r") as kca_freq_table_file:
                while(True):
                    line = kca_freq_table_file.readline()                    
                    if(len(line) == 0):
                        break
                    if(line[0] == "#"):
                        continue

                    split_line_array = line.split(",")

                    if(len(split_line_array) == 6):
                        service_provider = split_line_array[0]
                        kca_freq = split_line_array[1]
                        service_type = split_line_array[2]
                        bandwidth = split_line_array[3]                        
                        
                        key = service_provider + "_" + service_type + "_" + kca_freq                        
                        dict_data = {'key':key, 'bandwidth':bandwidth}
                        self.__kca_freq_table.append(dict_data)
                        print("added : ", dict_data)
                    else:
                        print("CSV Line Parsing Error : ", split_line_array)
        except:
            print("kca_freq_table.csv open failure")

# ============================================================================================================================
#   안테나 패턴명 설정 함수
# ============================================================================================================================
    def set_antenna_pattern_name_non_directional(self, horizontal_ant_name:str, vertical_ant_name:str):
        self.ant_name_non_dir_horizon = horizontal_ant_name
        self.ant_name_non_dir_vertical = vertical_ant_name

    def set_antenna_pattern_name_directional(self, horizontal_ant_name:str, vertical_ant_name:str):
        self.ant_name_directional_horizon = horizontal_ant_name
        self.ant_name_directional_vertical = vertical_ant_name

# ============================================================================================================================
# ============================================================================================================================
    def get_insert_query_column_list_single_azimuth(self) -> list:
        return self.insert_query_column_list_single_azimuth

    def get_insert_query_column_list_multiple_azimuth(self) -> list:
        return self.insert_query_column_list_multiple_azimuth

# ============================================================================================================================
# ============================================================================================================================
    def set_connection_info(self, host_address:str, port_num:int, username:str, password:str):
        """
        IRSS MySQL DB 에 연결을 위한 정보 설정
        """
        self.host_address = host_address
        self.port_num = port_num
        self.username = username
        self.password = password

# ============================================================================================================================
# ============================================================================================================================
    def connect(self) -> bool:
        """
        set_connection_info() 에 의해 설정된 연결정보에 따라 IRSS MySQL DB 에 연결    
        """
        try:
            self.conn = pymysql.connect(host=self.host_address, port=self.port_num, user=self.username, password=self.password, charset='utf8')
        except:
            print("IRSS DB Manager : DB Connection Failed")
            print(" -- ", self.host_address, self.port_num, self.username, self.password, self.db_name)
            return False

        self.cur = self.conn.cursor()
        self.connect_called = True
        return True

# ============================================================================================================================
# ============================================================================================================================
    def close_connection(self):
        """
        DB 연결 끊기.
        """
        if(self.connect_called == True):
            self.conn.close()
            self.connect_called = False

# ============================================================================================================================
# ============================================================================================================================
    def do_query(self, query_str) -> int:
        if(self.connect_called == False):
            print("IRSS DB Manager / do_query() : Called without connect()")
            return 0

        try:
            self.cur.execute(query_str)
            self.conn.commit()
            return 1
        except:
            return 0

# ============================================================================================================================
# ============================================================================================================================
    def do_truncate_all_table(self, service_provider_list, service_type_list):
        if(self.connect_called == False):
            print("IRSS DB Manager / do_truncate_all_table() : Called without connect()")
            return

        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit()        

        for serv_provider_name in service_provider_list:
            for serv_type_name in service_type_list:  
                table_name = self.table_name_prefix_analysis_completed + serv_provider_name + "_" + serv_type_name
                sql_query_str = "TRUNCATE " + table_name
                self.cur.execute(sql_query_str)
                self.conn.commit()  

                table_name = self.table_name_prefix_update_required + serv_provider_name + "_" + serv_type_name
                sql_query_str = "TRUNCATE " + table_name
                self.cur.execute(sql_query_str)
                self.conn.commit()  

# ============================================================================================================================
# ============================================================================================================================
    def create_irss_database(self):
        if(self.connect_called == False):
            print(" ** Error) IRSS DB Manager / create_irss_database() : Called without connect()")
            return

        sql_query_str = "CREATE DATABASE IF NOT EXISTS " + self.db_name
        self.cur.execute(sql_query_str)
        self.conn.commit()

# ============================================================================================================================
# ============================================================================================================================
    def create_db_table_tbl(self, base_table_name:str):
        """
        DB 테이블 생성 함수.
        Args:
            base_table_name : 테이블이름
                              내부적으로는 "base_table_name" 및 "update_[base_table_name]"을 생성한다.
        Return:
            없음
        """
        if(self.connect_called == False):
            print(" ** Error) IRSS DB Manager / create_db_table_scenario_tbl() : Called without connect()")
            return

        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit()     

        # 갱신 필요 DB
        sql_query_str = "CREATE TABLE IF NOT EXISTS " + self.table_name_prefix_update_required + base_table_name + \
                            " (" + self.common_sql_query_str + ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"
        self.cur.execute(sql_query_str)  # 커서로 sql문 실행
        self.conn.commit()

        # 갱신 필요 DB의 링크 테이블 (HTZ 입력 위해 필요)
        sql_query_str = "CREATE TABLE IF NOT EXISTS " + self.table_name_prefix_update_required + base_table_name + "_lks" + \
                            " (" + self.htz_link_tbl_create_query_str + ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"
        self.cur.execute(sql_query_str)  # 커서로 sql문 실행
        self.conn.commit()

        # 완료 DB
        sql_query_str = "CREATE TABLE IF NOT EXISTS " + self.table_name_prefix_analysis_completed + base_table_name + \
                            " (" + self.common_sql_query_str + ") ENGINE=InnoDB DEFAULT CHARSET=utf16;"
        self.cur.execute(sql_query_str)  # 커서로 sql문 실행
        self.conn.commit()

# ============================================================================================================================
# ============================================================================================================================
    def get_num_of_rows_in_update_req_table(self, base_table_name:str) -> int:
        if(self.connect_called == False):
            print(" ** Error) IRSS DB Manager / get_num_of_rows_in_update_req_table() : Called without connect()")
            return -1

        # USE [DB 이름]
        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit()     

        update_req_table_name = self.table_name_prefix_update_required + base_table_name

        sql_query_str = "SELECT * FROM " + update_req_table_name
        try:
            self.cur.execute(sql_query_str)
            self.conn.commit()
        except:
            print("Query fail : ", sql_query_str)
            return -2

        query_result_rows = self.cur.fetchall()

        return len(query_result_rows)

# ============================================================================================================================
# ============================================================================================================================
    def overwrite_update_req_table_into_complete_table(self, base_table_name:str) -> int:
        if(self.connect_called == False):
            print(" ** Error) IRSS DB Manager / overwrite_update_req_table_into_complete_table() : Called without connect()")
            return

        # USE [DB 이름]
        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit()     

        update_req_table_name = self.table_name_prefix_update_required + base_table_name
        complete_table_name = self.table_name_prefix_analysis_completed + base_table_name

        # 1) 업데이트 요청 DB에서 Info1의 목록(=대상 [기지국 식별자]_[각도])을 획득
        sql_query_str = "SELECT * FROM " + update_req_table_name
        try:
            self.cur.execute(sql_query_str)
            self.conn.commit()
        except:
            print("Query fail : ", sql_query_str)
            return False

        query_result_rows = self.cur.fetchall()
        
        target_info1_list = []
        for table_row in query_result_rows:
            info1_rds_pms_no = table_row[self.key_column_index_info1]

            # ICS_VALUE 열 (101번째)이 비어있지 않다면 이동.
            if(table_row[self.column_index_ics_value] == None):
                print(info1_rds_pms_no, "is not analyzed by HTZ. Remaining it.")
            else:                
                target_info1_list.append(info1_rds_pms_no)

        # 2) 완료 DB에 Info1과 동일 항목이 있을 경우 모두 삭제 (기존 결과 삭제)
        #    INFO1 : [기지국번호]_[각도]
        for target_info1 in target_info1_list:
            sql_query_str = "DELETE FROM " + complete_table_name + (" WHERE INFO1=\"%s\"" % target_info1)
            try:
                self.cur.execute(sql_query_str)
                self.conn.commit()
            except:
                print("Query fail : ", sql_query_str)
                return False

        # 3) 요청 DB 내용 --> 완료 DB 이동 및 요청 DB에서 지우기
        # TODO : ID 중복 처리 (PRIMARY KEY라서 중복 불가)
        for target_info1 in target_info1_list:
            # 요청 DB 내용 --> 완료 DB 이동
            sql_query_str = "INSERT INTO " + complete_table_name + " SELECT * FROM " + update_req_table_name + (" WHERE INFO1=\"%s\"" % target_info1)
            try:
                self.cur.execute(sql_query_str)
                self.conn.commit()
            except:
                print("Query fail : ", sql_query_str)
                return False

            # 이동된 요청 DB 내용 지우기
            sql_query_str = "DELETE FROM " + update_req_table_name + (" WHERE INFO1=\"%s\"" % target_info1)
            try:
                self.cur.execute(sql_query_str)
                self.conn.commit()
            except:
                print("Query fail : ", sql_query_str)
                return False

# ============================================================================================================================
# ============================================================================================================================
    def insert_kca_json_entry_into_update_req_table_v2(self, base_table_name:str, kca_json_entry, Cus_cd:str) -> bool:                
        """
        HTZ 분석 요구 테이블에 항목을 추가하는 함수

        Args:
            base_table_name : 테이블명
                내부적으로는 "update_[테이블명]"에 삽입함
                테이블 이름은 HTZ 실행 단위에 대응하는 테이블이어야 한다.

            kca_json_entry : KCA의 JSON 데이터에서 "RESULT" 부분(복수개) 내 한개 항목 개체

        Return:
            없음
        """
        if(self.connect_called == False):
            print("*** Error : IRSS DB Manager / insert_kca_json_entry_into_update_req_table_v2() : Called without connect()")
            return

        target_db_table_name = self.table_name_prefix_update_required + base_table_name

        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit()

        # HTZ추가 전, INFO에 대해 기 추가된 요청이 있는지 확인.
        # 있을 경우 삭제 (본 정보가 최신이므로)
        try:
            rds_pms_no = kca_json_entry.get("RDS_PMS_NO") 
        except:
            return False                           
        
        sql_query_str1 = "SELECT * FROM " + target_db_table_name + (" WHERE INFO1 like \"%s%%\"" % (rds_pms_no))      # % -> rds_pms_no 포함하는거 검색
        self.cur.execute(sql_query_str1)
        self.conn.commit()
        # print(sql_query_str1)

        sql_query_rows = self.cur.fetchall()

        if(len(sql_query_rows) > 0):
            # 대응 항목이 이미 있다면 신규 데이터만 유효하므로 삭제
            # TODO : 테이블에 해당 항목이 있는건 오류 상황일 가능성 높음
            for column_idx in range(0, len(sql_query_rows)):
                id = int(sql_query_rows[column_idx][self.key_column_index_id])
                info1 = sql_query_rows[column_idx][self.key_column_index_info1]
                sql_query_str2 = "DELETE FROM " + target_db_table_name + " WHERE ID=%d and INFO1=\"%s\"" % (id, info1)
                # print(sql_query_str2)
                self.cur.execute(sql_query_str2)
                self.conn.commit()

        # KCA로 부터 받은 json 항목에 있는 값을 얻어놓기
        Rds_pms_no = str(kca_json_entry.get("RDS_PMS_NO"))      # 기지국 식별자
        Service_cd = str(kca_json_entry.get("SERVICE_CD"))      # 서비스 제공자
        Freq_mhz = str(kca_json_entry.get("FRQ_HZ"))          # 주파수        
        Altitude = str(kca_json_entry.get("ALT_ALTD_HET"))      # 고도
        if "None" in Altitude:
            Altitude = None

        Nominal_power = str(kca_json_entry.get("ARW_PWR_WTT"))  # ARW_PWR_WTT 재정의
        if "None" in Nominal_power:
            Nominal_power = None

        Gain = str(kca_json_entry.get("ARW_GAIN"))  # ARW_GAN_NMV 재정의
        if "None" in Gain:
            Gain = None
        Gain_rx = Gain

        Height_antenna = str(kca_json_entry.get("GND_ALTD_HET"))  # GND_ALTD_HET 재정의
        if "None" in Height_antenna:
            Height_antenna = None        

        Address_str = str(kca_json_entry.get("RDS_TRS_ADR"))  # RDS_TRS_ADR 크기가 길어서 50 이상이면 자르기
        if len(Address_str) >= 50:
            Address_str = Address_str[:50]
        
        Date_serv = str(kca_json_entry.get("SYS_CHG_DTM"))    # 날짜 : 20/01/11 --> 20200111
        Date_serv = Date_serv.replace("/","")
        Date_serv = "20"+ Date_serv

        rds_sta_cd = str(kca_json_entry.get("RDS_STA_CD"))      # 기지국 상태
        if(rds_sta_cd == "00"):
            Icst_status = 6
        elif(rds_sta_cd == "01"):
            Icst_status = 11
        elif(rds_sta_cd == "02"):
            Icst_status = 15
        else:
            Icst_status = None

        Longitude = str(kca_json_entry.get("LON"))           # 경도, 위도 --> 도분초 표시 제거 (Decimal 변환은 하지 않음)
        Latitude = str(kca_json_entry.get("LAT"))

        Longitude = Longitude.replace(".","") 
        Longitude = Longitude.replace("'","")
        Longitude = Longitude.replace(" ","")
        Longitude = Longitude.replace("\\", "")
        Longitude = Longitude.replace("\"", "")
        Longitude = Longitude.replace("°", ".", 1)

        Latitude = Latitude.replace(".","") 
        Latitude = Latitude.replace("'","")
        Latitude = Latitude.replace(" ","")
        Latitude = Latitude.replace("\\", "")
        Latitude = Latitude.replace("\"", "")
        Latitude = Latitude.replace("°", ".", 1)

        # 통신사/기술 무관 DB 삽입 상수값
        Losses = 0
        Losses_rx = 0
        Fktb = -97                  # 열잡음
        Tilt = -3

        # 통신사/기술 관련 DB 삽입값 찾기 : Bandwidth, Bandwidth_rx
        # __init__ 에서 .csv 파일을 읽어서 만들어둔 테이블과 비교
        Bandwidth = None
        Bandwidth_rx = None

        key = Cus_cd + "_" + Service_cd + "_" + Freq_mhz
        for idx, kca_freq_map_entry in enumerate(self.__kca_freq_table):
            if(key == kca_freq_map_entry['key']):
                Bandwidth = kca_freq_map_entry['bandwidth']
                Bandwidth_rx = Bandwidth
                break          

        if(Bandwidth == None):
            print("Warning : 대역폭정보 없음 (사업자_기술_주파수=", key, ")")

        # SERVICE_CD (2G ~ 5G) 별 값 (Threshold, Threshold_rx, Category)
        # --- 2G ----
        if(Service_cd == "2G"):
            Pilot = None
            Threshold = -100            
            if(Cus_cd == "LG"):             # LG 2G
                Category = 38
            else:
                Category = None             # SK 2G, KT 3G : 서비스 종료임.         
        # --- 3G ----
        elif(Service_cd == "3G"):
            Pilot = 10
            Threshold = -115            
            if(Cus_cd == "LG"):             # LG 3G
                Category = 37
            elif(Cus_cd == "SK" or Cus_cd == "KT"):     # SK 3G / KT 3G
                Category = 35
            else:
                Category = None
        # --- 4G ----
        elif(Service_cd == "4G"):
            Pilot = 5.562
            Threshold = -140            
            Category = 60                   
        # --- 5G ----
        elif(Service_cd == "5G"):
            Pilot = None
            Threshold = -156
            Category = 104
        else:
            Pilot = None
            Threshold = None
            Category = None

        Threshold_rx = Threshold

        # Info2 : 설치형태
        Info2_ARW_FORM_CD = str(kca_json_entry.get("ARW_FORM_CD"))

        # Info3 : 통신사 + 서비스
        #         Cus_cd는 조회했을때 쓴 것 보다는 맵핑된 것 사용
        Info3_CUS_CD_and_SERVICE_CD = Cus_cd + "_" + Service_cd

        # Call sign 공통부분
        # 기지국 허가번호 뒤에서 5자리 + "-" + 년도 2자리 + "(000)"
        # 예) #####-YY(000)
        base_call_sign = Rds_pms_no[-5:] + "-" + Rds_pms_no[4:6] + "(000)"  

        # 방향각도 별 처리 시작.
        # 복수개인 경우 목록화 --> 나중에 Call sign에 a, b, c, ... 붙이기
        #CALL_SIGN에 a, b, c, d,  등을 삽입하기 위해        

        azimuth_full_str = str(kca_json_entry.get("ARW_AIM_ANG_CTN"))   # Azimuth 문자열 획득
        azimuth_full_str.replace("//","/")                              # 값이 //로 들어있는 오류를 제거하기 위해 삽입
        azimuth_str_array = azimuth_full_str.split("/")                 # /을 기준으로 나누기
        
        # DB에 삽입
        # AZIMUTH 가 2개 이상인 경우 CALL_SIGN에 a, b, c, 로 늘려서 나누어 줘야 함.
        if(len(azimuth_str_array) >= 2) : 
            for idx, azimuth_str in enumerate(azimuth_str_array):
                # 분할된 Azimuth 값이 숫자인지 확인
                try:
                    azimuth_int = int(azimuth_str)
                except:
                    azimuth_int = None

                # 분할된 Azimuth 값이 숫자인지 확인
                if(azimuth_int == None):
                    AZ_str = "None"             # Azimuth가 문자인 경우 (ex. ND, N/D, 무지향, ...) --> None
                    Antenna_nameH = self.ant_name_non_dir_horizon
                    Antenna_nameV = self.ant_name_non_dir_vertical               
                else:
                    AZ_str = str(azimuth_int)   # Azimuth가 숫자인 경우
                    Antenna_nameH = self.ant_name_directional_horizon
                    Antenna_nameV = self.ant_name_directional_vertical

                # Call sign
                call_sign_alphabet = self.__alphabet_list[idx]
                Call_sign = base_call_sign + call_sign_alphabet #CALL_SIGN 바꾸는 작업 + 중복 피하기 위해 알파벳 붙이기

                INFO1_RDS_PMS_NO_and_Idx_and_AZ = Rds_pms_no + "_" + str(idx + 1) + "_" + str(AZ_str)

                sql_query_str = "INSERT INTO "+ target_db_table_name + \
                    "(" + self.sql_column_string_multiple_azimuth + ") " \
                    "VALUES (" + self.sql_values_input_string_multiple_azimuth + ")"                

                val = [(Call_sign, Address_str, '4DMS', Longitude, Latitude, 
                        Altitude, Nominal_power, Gain, Gain_rx, Losses, 
                        Losses_rx, Freq_mhz, Height_antenna, Threshold, Threshold_rx, 
                        Bandwidth, Bandwidth_rx, INFO1_RDS_PMS_NO_and_Idx_and_AZ, Info2_ARW_FORM_CD, Date_serv, 
                        Icst_status, azimuth_int, Info3_CUS_CD_and_SERVICE_CD, Category, Pilot, 
                        Fktb, Antenna_nameH, Antenna_nameV, Antenna_nameH, Antenna_nameV, 
                        0, Tilt)]

                try:
                    self.cur.executemany(sql_query_str, val)
                    self.conn.commit()
                except:               
                    print("IRSS DB Manager query fail : " + INFO1_RDS_PMS_NO_and_Idx_and_AZ)
            # --- end for idx, azimuth_str in enumerate(azimuth_str_array): ---------------------------------------------------------
                
        else : #AZIMUTH 1개인 경우
            azimuth_str = azimuth_str_array[0]

            # 분할된 Azimuth 값이 숫자인지 확인
            try:
                azimuth_int = int(azimuth_str)
            except:
                azimuth_int = None

            if(azimuth_int == None):
                AZ_str = "None"             # Azimuth가 문자인 경우 (ex. ND, N/D, 무지향, ...) --> 무지향안테나
                Antenna_nameH = self.ant_name_non_dir_horizon
                Antenna_nameV = self.ant_name_non_dir_vertical               
            else:
                AZ_str = str(azimuth_int)   # Azimuth가 숫자인 경우 --> 지향성 안테나
                Antenna_nameH = self.ant_name_directional_horizon
                Antenna_nameV = self.ant_name_directional_vertical

            # Call sign
            Call_sign = base_call_sign

            idx = 0
            INFO1_RDS_PMS_NO_and_Idx_and_AZ = Rds_pms_no + "_" + str(idx + 1) + "_" + str(AZ_str)

            sql_query_str = "INSERT INTO "+ target_db_table_name + \
                    "(" + self.sql_column_string_single_azimuth + ") " \
                    "VALUES (" + self.sql_values_input_string_single_azimuth + ")"

            val = [(Call_sign, Address_str, '4DMS', Longitude, Latitude, 
                        Altitude, Nominal_power, Gain, Gain_rx, Losses, 
                        Losses_rx, Freq_mhz, Height_antenna, Threshold, Threshold_rx, 
                        Bandwidth, Bandwidth_rx, INFO1_RDS_PMS_NO_and_Idx_and_AZ, Info2_ARW_FORM_CD, Date_serv, 
                        Icst_status, azimuth_int, Info3_CUS_CD_and_SERVICE_CD, Category, Pilot, 
                        Fktb, 0, Tilt)]

            # 쿼리를 통해 마리아 DB 데이터 입력
            try:
                self.cur.executemany(sql_query_str, val)
                self.conn.commit() 
            except:
                print("IRSS DB Manager query fail : " + INFO1_RDS_PMS_NO_and_Idx_and_AZ)
        # == end if(len(AZARR) >= 2) : ===========================================

        return True