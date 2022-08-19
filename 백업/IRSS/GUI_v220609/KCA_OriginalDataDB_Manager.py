from ctypes.wintypes import LONG
import json
import pymysql
import os
from datetime import datetime

class KCA_OriginalDataDB_Manager(object):
    def __init__(self):
        self.db_name = "irss_db"
        self.table_name = "kca_original_data_tbl"

        now = datetime.now()
        self.logfile_name = "log_kca_origdb_" + str(now.year) + str(now.month) + str(now.day) + ".log"        

        # KCA의 JSON 파일 내 기지국 1개 당 데이터 항목을 DB 테이블 column 순으로 정리한 것
        self.kcs_json_entry_name_list = ["RDS_PMS_NO", "RDS_TRS_ADR", "SERVICE_CD", "LON", "LAT", \
                                    "FRQ_HZ", "ARW_PWR_WTT", "ARW_FORM_CD", "ARW_GAIN", "ALT_ALTD_HET", \
                                    "GND_ALTD_HET", "EXPS_ALTD_HET", "ARW_AIM_ANG_CTN", "RDS_STA_CD", "SYS_CHG_DTM"]

        # 테이블 생성 및 파싱에 쓰이는 Column 이름 목록 및 Column 길이
        # 비교처리에는 해당 데이터를 쓰지 않으므로 수정사항 발생시 해당 부분 찾아서 고칠것        
        self.db_table_column_list = ["RDS_PMS_NO", "RDS_TRS_ADR", "SERVICE_CD", "LON", "LAT", \
                                    "FRQ_HZ", "ARW_PWR_WTT", "ARW_FORM_CD", "ARW_GAIN", "ALT_ALTD_HET", \
                                    "GND_ALTD_HET", "EXPS_ALTD_HET", "ARW_AIM_ANG_CTN", "RDS_STA_CD", "SYS_CHG_DTM", \
                                    "CUS_CD"]
        self.db_table_column_length_list = [20, 100, 10, 20, 20, \
                                            10, 50, 50, 10, 10, \
                                            10, 10, 50, 15, 15,
                                            20]

        self.primary_key = "RDS_PMS_NO"

        # JSON -> list 파싱한 것에 대해 주요 정보의 index
        self.rds_pms_no_index = 0           # RDS_PMS_NO의 list index. 기지국 식별자
        self.rds_sta_cd_no_index = 13       # RDS_STA_CD의 list index. 허가상태 부분
        self.sys_chg_dtm_index = 14         # SYS_CHG_DTM의 list index. 정보변경일 부분
        self.cus_cd_index = 15              # CUS_CD list index. 사업자 (* JSON에는 해당 정보 없음)

        self.host_address = ""
        self.port_num = 3307
        self.username = ""
        self.password = ""

    def __write_log_into_file(self, log_text, display_to_stdout:bool=False):
        """
        로그 텍스트를 파일로 저장.
        마지막에 개행문자를 삽입해주므로, 입력에는 개행문자를 생략할 것.
        """
        if(os.path.exists(".\\logs_kca_orig_db") == False):
            print("create folder : logs_kca_orig_db")
            os.makedirs(".\\logs_kca_orig_db")

        now = datetime.now()
        self.logfile_name = ".\\logs_kca_orig_db\\log_kca_origdb_" + str(now.year) + str(now.month) + str(now.day) + ".log"  
        time_str = str(now.year) + "/" + str(now.month) + "/" + str(now.day) + "-" + \
                    str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + ") "

        with open(self.logfile_name, 'a') as logfile:
            logfile.write(time_str + log_text + '\n')

        if(display_to_stdout):
            print(time_str + log_text + '\n')

    def get_kcs_json_entry_list(self) -> list:
        return self.kcs_json_entry_name_list
            
    def set_connection_info(self, host_address, port_num, username, password):
        self.host_address = host_address
        self.port_num = port_num
        self.username = username
        self.password = password

    def connect(self) -> bool:        
        """
        DB에 연결하는 함수
        """
        try:
            self.conn = pymysql.connect(host=self.host_address, port=self.port_num, user=self.username, password=self.password, charset='utf8')
        except:
            return False

        self.cur = self.conn.cursor()
        return True        

    def close_db_connection(self):
        """
        DB에 연결을 끊는 함수
        """
        self.conn.close()

    def do_truncate_all_table(self):
        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit() 

        sql_query_str = "TRUNCATE " + self.table_name
        self.cur.execute(sql_query_str)
        self.conn.commit()

    def initialize_db_table_if_not_exists(self):        
        # DB가 없으면 만들기
        sql_query_str = "CREATE DATABASE IF NOT EXISTS " + self.db_name
        self.cur.execute(sql_query_str)
        self.conn.commit()

        # USE 구문으로 데이터베이스 사용 선언
        sql_query_str = "USE " + self.db_name 
        self.cur.execute(sql_query_str)
        self.conn.commit()

        # CREATE TABLE IF NOT EXISTS 구문으로 날려서 테이블 만들기
        sql_query_str = "CREATE TABLE IF NOT EXISTS `" + self.table_name + "` (" \

        for idx, column_name in enumerate(self.db_table_column_list):
            if(column_name == self.primary_key):
                sql_query_str = sql_query_str + ("\n`%s` varchar(%d) UNIQUE," % (column_name, self.db_table_column_length_list[idx]))
            else:
                sql_query_str = sql_query_str + ("\n`%s` varchar(%d) DEFAULT NULL," % (column_name, self.db_table_column_length_list[idx]))
   
        sql_query_str = sql_query_str + "\nPRIMARY KEY (`%s`) );" % (self.primary_key)

        # print(sql_query_str)
        self.cur.execute(sql_query_str)
        self.conn.commit()

    # ========================================================================================================================
    def create_parsed_list_from_kca_json_entry(self, kca_json_entry) -> list:
        """
        KCA JSON 내 RESULT 리스트의 하나 항목을 분리하여 "파싱된 리스트"로 만들어줌
        """
        parsed_entry_list = []
        for idx, column_name in enumerate(self.kcs_json_entry_name_list):
            entry_data = kca_json_entry.get(column_name)

            if(entry_data is None):
                entry_data = ""

            if(column_name == "LON" or column_name == "LAT"):           # LON또는 LAT의 경우 처리
                entry_data = entry_data.replace(" ", "")
                entry_data = entry_data.replace("°", ":")
                entry_data = entry_data.replace("\'", ":")
                entry_data = entry_data.replace("\"", "")

            parsed_entry_list.append(entry_data)

        return parsed_entry_list

    # ========================================================================================================================
    def update_to_db_from_parsed_entry_list(self, parsed_entry_list, cus_cd:str="") -> int:
        """
        파싱된 리스트"를 입력받아 KCA 원본 DB 항목을 갱신
        테이블에 RDS_PMS_NO가 동일한 것이 있는 경우에만 호출할 것.
        """
        # UPDATE [테이블] SET A=a, B=b, ... WHERE RDS_PMS_NO="" 구문 사용
        sql_query_str = "UPDATE " + self.table_name + " SET "
        
        # A=a, B=b, ... 부분 붙이기
        rds_pms_no = ""
        first_value_set = False
        for idx, entry_read in enumerate(parsed_entry_list):
            if(first_value_set):
                sql_query_str = sql_query_str + ", "

            if(self.db_table_column_list[idx] == self.db_table_column_list[self.rds_pms_no_index]):         # RDS_PMS_NO 항목인 경우 -> where 뒤로 이동
                rds_pms_no = entry_read
            else:
                sql_query_str = sql_query_str + self.db_table_column_list[idx] + "=" + ("\"%s\"" % (entry_read))
                first_value_set = True

        # parsed_entry_list에는 없는 CUS_CD 처리
        sql_query_str = sql_query_str + ", %s=\"%s\"" % (self.db_table_column_list[self.cus_cd_index], cus_cd)

        # 뒤에 Where 붙이기
        sql_query_str = sql_query_str + " WHERE " + "%s=%s" % (self.db_table_column_list[self.rds_pms_no_index], rds_pms_no)

        try:
            self.cur.execute(sql_query_str)
            self.conn.commit()
            return 1
        except:
            self.__write_log_into_file("  ** UPDATE Query Failed : %s" % (sql_query_str), True)
            return 0

    def insert_to_db_from_parsed_entry_list(self, parsed_entry_list, cus_cd:str="") -> int:
        """
        파싱된 리스트"를 입력받아 KCA 원본 DB 항목에 추가
        테이블에 RDS_PMS_NO가 동일한 것이 없는 경우 호출
        """
        sql_query_str = "INSERT INTO " + self.table_name + " VALUES ("

        # 인자로 들어온 리스트에 있는거 차곡차곡 채우기 (마지막 CUS_CD는 없음)
        for idx, entry_read in enumerate(parsed_entry_list):              
            if(idx == 0):
                sql_query_str = sql_query_str + "\"%s\"" % (entry_read)
            else:
                sql_query_str = sql_query_str + ", \"%s\"" % (entry_read)

        # CUS_CD 처리 : JSON 데이터에 미포함이기 때문에 인자로 받은 것을 사용
        sql_query_str = sql_query_str + ", \"%s\"" % (cus_cd)

        sql_query_str = sql_query_str + ")" 

        # 쿼리 날리기
        try:
            self.cur.execute(sql_query_str)
            self.conn.commit()
            return 1
        except:
            self.__write_log_into_file("  ** INSERT Query Failed : %s" % (sql_query_str), True)
            return 0

    def decide_job_from_parsed_entry_list(self, parsed_entry_list) -> tuple[int, int]:
        """
        KCA 원본정보 데이터에 대해 기존에 저장된 정보와 비교하여 필요한 조치를 결정하여 반환한다

        Args:
        parsed_entry_list : DB 테이블 Column 순서대로 입력값이 들어있는 리스트 (CUS_CD 제외).
                            KCA JSON 포맷에서 얻은 json 항목을 create_parsed_list_from_kca_json_entry() 함수에 입력하여 획득 가능.
                            참고로, 본 클래스의 get_kcs_json_entry_list() 호출시 대응되는 DB 테이블 상 column 목록이 리턴됨.
        Returns: [kca_original_db_job_req, required_htz_db_job]
            <kca_original_db_job_req>
                0 : 추가작업 불필요
                1 : KCA Original DB에 항목 Insert 필요
                2 : KCA Original DB에 항목 Update 필요 (기지국 허가 상태)
                3 : KCA Original DB에 항목 Update 필요 (기지국이 휴지/정지 상태로 변경됨)
            <required_htz_db_job>
                0 : 분석 필요 없음
                1 : 분석 갱신 필요 (신규)
                2 : 분석 갱신 필요 (기존 기지국 데이터 변경 있음)
                3 : 기존 분석 결과 삭제 조치 필요 (기지국이 정지로 변경된 경우)
        """
        rds_pms_no = parsed_entry_list[self.rds_pms_no_index]                   # 기지국 식별자
        rds_sta_cd_new = int(parsed_entry_list[self.rds_sta_cd_no_index])       # 상태 (00 : 허가, 01 : 휴지, 02 : 정지)

        sql_query_str = "USE " + self.db_name + ";"
        try:
            self.cur.execute(sql_query_str)      
            self.conn.commit()  
        except:
            self.__write_log_into_file(" ** USE Query Failed : %s" % (sql_query_str), True)

        # Select 쿼리 날려서 기존에 있는것 획득
        sql_query_str = "SELECT * FROM " + self.table_name + " WHERE RDS_PMS_NO=\"%s\";" % (rds_pms_no)
        try:
            self.cur.execute(sql_query_str)
            self.conn.commit()
        except:
            self.__write_log_into_file(" ** SELECT Query Failed : %s" % (sql_query_str), True)

        rows = self.cur.fetchall()

        # == 추가/갱신/삭제 여부 판정 작업 시작 =================================================
        return_code_kca_orig_db_job = 0                 # 기본 : 추가작업 불필요
        return_code_htz_db_job = 0                      # 기본 : HTZ 분석 필요 없음
        if(len(rows) > 1):
            # 하나의 RDS_PMS_NO에 복수개가 검색되었음 --> 오류 상황
            self.__write_log_into_file("RDS_PMS_NO %s : Delete all and Insert Required (Data error)" % (rds_pms_no), True)
            
            try:
                sql_query_str = "DELETE FROM " + self.table_name + " WHERE RDS_PMS_NO=\"%s\"" % (rds_pms_no)
                self.cur.execute(sql_query_str)
            except:
                self.__write_log_into_file(" ** DELETE Query Failed : %s" % (sql_query_str), True)

            return_code_kca_orig_db_job = 1             # Insert 필요
            return_code_htz_db_job = 1                  # KCA DB 갱신 필요
        elif(len(rows) == 1):
            # 1개 : 최신 여부 확인 필요
            sys_chg_dtm_old:str = rows[0][self.sys_chg_dtm_index]
            sys_chg_dtm_new:str = parsed_entry_list[self.sys_chg_dtm_index]
            sys_chg_dtm_old = sys_chg_dtm_old.replace("/", "")
            sys_chg_dtm_new = sys_chg_dtm_new.replace("/", "")
            rds_sta_cd_old = int(rows[0][self.rds_sta_cd_no_index])

            if(int(sys_chg_dtm_new) > int(sys_chg_dtm_old)):            # 최근 것인 경우
                if(rds_sta_cd_new == 0):
                    # 날짜가 업데이트되었고, 허가인 경우에는 반드시 수행
                    self.__write_log_into_file("RDS_PMS_NO %s : Date Updated (%s -> %s))" % (rds_pms_no, sys_chg_dtm_old, sys_chg_dtm_new))
                    return_code_kca_orig_db_job = 2                     # KCA 원본 기존 데이터 업데이트 필요
                    return_code_htz_db_job = 2                          # HTZ 분석 필요 (업데이트)
                elif(rds_sta_cd_old == 0 and rds_sta_cd_new != 0):
                    # 허가 --> 정지인 경우
                    self.__write_log_into_file("RDS_PMS_NO %s : Update Required(Enabled --> Disabled)" % (rds_pms_no))
                    return_code_kca_orig_db_job = 3                     # KCA 원본 기존 데이터 업데이트 필요
                    return_code_htz_db_job = 3                          # 기존 HTZ 분석 데이터 삭제/비활성 필요
                else:
                    # 날짜가 변경되었으나 활성화/비활성화 여부는 변동이 없음
                    # TODO : 활성화인 기지국인 경우 전체 내용 비교 필요?
                    return_code_kca_orig_db_job = 0
                    return_code_htz_db_job = 0
                    pass
            else:                                                       # 아닌 경우
                # 기존에 1개가 있으며, 날짜 변경이 없음
                return_code_kca_orig_db_job = 0
                return_code_htz_db_job = 0
                self.__write_log_into_file("RDS_PMS_NO %s : Skip" % (rds_pms_no))
        else:
            # 기존 데이터 0개 : 데이터 추가 필요
            if(rds_sta_cd_new == 0):
                # 허가상태 기지국인 경우 추가 필요
                self.__write_log_into_file("RDS_PMS_NO %s : Insert Required (New Data)" % (rds_pms_no))
                return_code_kca_orig_db_job = 1 
                return_code_htz_db_job = 1
            else:
                # 비활성 상태 기지국인 경우에는 KCA 원본 DB 에만 추가
                self.__write_log_into_file("RDS_PMS_NO %s : Insert Required (New Data / Non-active BS)" % (rds_pms_no))
                return_code_kca_orig_db_job = 1
                return_code_htz_db_job = 0
                pass
       
        return [return_code_kca_orig_db_job, return_code_htz_db_job]