from tkinter import *
import tkinter
import os
import sys
from datetime import datetime
from time import *
import json
import threading
import subprocess

from HTZInputDBManager import HTZInputDBManager
from KCA_Connection_Manager import KCA_Connection_Manager
from KCA_OriginalDataDB_Manager import KCA_OriginalDataDB_Manager

class KCA_Connection_UI(object):
    def __init__(self):
        self.kca_conn_manager = KCA_Connection_Manager()        
        self.irss_db_manager = HTZInputDBManager()
        self.kca_originaldatadb_manager = KCA_OriginalDataDB_Manager()

        self.filename_kca_conn_ini = "kca_connection_info.ini"
        self.filename_irss_db_conn_ini = "irss_connection_info.ini"

        # ini 파일이 없을 경우 Database (schema) 이름 기본값
        self.db_name = "irss_db"

        self.root = Tk()
        self.root.title("KCA 접속 및 HTZ 입력 DB 구성 프로그램")         # 창 이름
        self.window_width = 800
        self.window_height = 600
        self.root.geometry("%dx%d" % (self.window_width, self.window_height))               # 창 크기?
        self.root.resizable(False, False)                   # 창 크기 변경 가능 여부   

        # 체크박스용 variables
        self.res_serv_prov_sk = IntVar(value=1)
        self.res_serv_prov_kt = IntVar(value=1)
        self.res_serv_prov_lg = IntVar(value=1)
        self.res_serv_prov_list = ["SK", "KT", "LG"]        # 기본 체크 상태에 따른 출력 목록
        self.res_serv_type_2g = IntVar(value=1)
        self.res_serv_type_3g = IntVar(value=1)
        self.res_serv_type_4g = IntVar(value=1)
        self.res_serv_type_5g = IntVar(value=1)
        self.res_serv_type_list = ["2G", "3G", "4G", "5G"]
        self.res_bs_type_32 = IntVar(value=1)             # 기지국 : default on
        self.res_bs_type_85 = IntVar(value=0)             # 중계기 : default off
        self.res_bs_type_list = ["32"]

        # 내부 variables
        self.res_serv_prov_checkbox_var_list = [self.res_serv_prov_sk, self.res_serv_prov_kt, self.res_serv_prov_lg]
        self.res_serv_prov_checkbox_key_list = ["SK", "KT", "LG"]       # full set 목록으로도 사용함

        self.res_serv_type_checkbox_var_list = [self.res_serv_type_2g, self.res_serv_type_3g, self.res_serv_type_4g, self.res_serv_type_5g]
        self.res_serv_type_checkbox_key_list = ["2G", "3G", "4G", "5G"]

        self.res_bs_type_checkbox_var_list = [self.res_bs_type_32, self.res_bs_type_85]
        self.res_bs_type_checkbox_key_list = ["32", "85"]        

        self.timer = None
        self.timer_is_on = 0
        self.job_is_ongoing = 0
        self.stop_button_pressed = 0

        now = datetime.now()
        self.logfile_name = "log_kca_origdb_" + str(now.year) + str(now.month) + str(now.day) + ".log"

        self.__timer_interval_sec = 60

    def __write_log_into_file(self, log_text, display_to_stdout:bool=False):
        """
        로그 텍스트를 파일로 저장.
        마지막에 개행문자를 삽입해주므로, 입력에는 개행문자를 생략할 것.
        """
        if(os.path.exists(".\\logs_gui") == False):
            print("create folder : logs_gui")
            os.makedirs(".\\logs_gui")

        now = datetime.now()
        self.logfile_name = ".\\logs_gui\\logs_gui_" + str(now.year) + str(now.month) + str(now.day) + ".log"  
        time_str = str(now.year) + "/" + str(now.month) + "/" + str(now.day) + "-" + \
                    str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + ") "

        with open(self.logfile_name, 'a') as logfile:
            logfile.write(time_str + log_text + '\n')

        if(display_to_stdout):
            print(time_str + log_text + '\n')

    def __read_kca_configuration_from_ini(self):
        # 처리 실패시 기본값 적용여부
        use_default = 1

        try:
            # kca_connection_info.ini 파일이 있으면 읽어서 바꾼다.
            with open(self.filename_kca_conn_ini, "r") as conn_ini_file:
                for i in range (0, 8):
                    line = conn_ini_file.readline()

                    # 줄이 부족한 경우 리턴, 기본값을 사용
                    if(len(line) == 0):
                        break

                    if(i==0):                               # line1 : 웹 주소
                        self.res_spectrummap_web_url = line.rstrip('\n')
                    elif(i==1):                             # line2 : 토큰 문자열
                        self.res_access_token_string = line.rstrip('\n')
                    elif(i==2):                             # line3 : 지역 목록
                        self.area_name_string = line.rstrip('\n')
                        tmp_str_splited = self.area_name_string.split(',')                        
                        self.res_area_name_list = []
                        for area_name in tmp_str_splited:
                            self.res_area_name_list.append(area_name)
                    elif(i==3):                             # line4 : 대상 연도 시작
                        self.res_year_from = int(line.rstrip('\n'))
                    elif(i==4):                             # line5 : 대상 연도 끝
                        self.res_year_to = int(line.rstrip('\n'))
                    elif(i==5):                             # line6 : 서비스 제공자
                        tmp_str = line.rstrip('\n')
                        self.res_serv_prov_list = tmp_str.split(",")
                        for checkbox_var in self.res_serv_prov_checkbox_var_list:
                            checkbox_var.set(0)
                        for ini_word in self.res_serv_prov_list:
                            for idx_key, key in enumerate(self.res_serv_prov_checkbox_key_list):
                                if(ini_word == key):
                                    checkbox = self.res_serv_prov_checkbox_var_list[idx_key]
                                    checkbox.set(1)      
                                    break
                    elif(i==6):                             # line7 : 서비스 유형(2G ~ 5G)
                        tmp_str = line.rstrip('\n')
                        self.res_serv_type_list = tmp_str.split(',')
                        for checkbox_var in self.res_serv_type_checkbox_var_list:
                            checkbox_var.set(0)
                        for ini_word in self.res_serv_type_list:
                            for idx_key, key in enumerate(self.res_serv_type_checkbox_key_list):
                                if(ini_word == key):
                                    checkbox = self.res_serv_type_checkbox_var_list[idx_key]
                                    checkbox.set(1)      
                                    break
                    elif(i==7):                             # line8 : 국종 (기지국, 중계기)         
                        tmp_str = line.rstrip('\n')
                        self.res_bs_type_list = tmp_str.split(',')
                        for checkbox_var in self.res_bs_type_checkbox_var_list:
                            checkbox_var.set(0)
                        for ini_word in self.res_bs_type_list:
                            for idx_key, key in enumerate(self.res_bs_type_checkbox_key_list):
                                if(ini_word == key):
                                    checkbox = self.res_bs_type_checkbox_var_list[idx_key]
                                    checkbox.set(1)      
                                    break
                        use_default = 0
        except EnvironmentError:
             # irss_connection_info.ini 파일이 없음
            print("KCA INI file is not found : ")
            use_default = 1
        
        if(use_default):     
            # 중단된 경우 기본값을 설정    
            self.__write_log_into_file("Reset to default KCA configuration")
            self.res_spectrummap_web_url = "https://spectrummap.kr/openapiNew.do"
            self.res_access_token_string = ""
            self.res_area_name_list = ["김해시","창원시"]
            self.res_area_name_string = "김해시,창원시"
            self.res_year_from = 2020
            now = datetime.now()
            self.res_year_to = now.year
            for idx, check_var in enumerate(self.res_serv_prov_checkbox_var_list):      # SK, KT, LG : default on
                check_var.set(1)
            for idx, check_var in enumerate(self.res_serv_type_checkbox_var_list):      # 2G ~ 5G : default on
                check_var.set(1)
            self.res_bs_type_32.set(1)             # 기지국 : default on
            self.res_bs_type_85.set(0)             # 중계기 : default off

            self.res_serv_prov_list = ["SK", "KT", "LG"]        # 기본 체크 상태에 따른 출력 목록
            self.res_serv_type_list = ["2G", "3G", "4G", "5G"]
            self.res_bs_type_list = ["32", "85"]

    def __read_irss_db_configuration_from_ini(self):
        # irss_connection_info.ini 파일이 있으면 읽어서 바꾼다.
        use_default = 0

        try:            
            with open(self.filename_irss_db_conn_ini, "r") as conn_ini_file:                
                for i in range (0, 5):
                    line = conn_ini_file.readline()
                    
                    # 줄이 부족한 경우 리턴
                    if(len(line) == 0):
                        break

                    splitted_line = line.split(":")
                    if(splitted_line[0] == "hostname"):
                        self.result_hostname = splitted_line[1].rstrip('\n')
                    elif(splitted_line[0] == "port_number"):                        
                        try:
                            self.result_portnumber = int(splitted_line[1].rstrip('\n'))
                        except:
                            # 포트가 번호 형식이 아님. 파일이 잘못된 것으로 간주하고 기본값으로 되돌림
                            conn_ini_file.close()
                            if os.path.isfile(self.filename_irss_db_conn_ini):
                                os.remove(self.filename_irss_db_conn_ini)
                            use_default = 1
                            break                            
                    elif(splitted_line[0] == "username"):
                        self.result_username = splitted_line[1].rstrip('\n')
                    elif(splitted_line[0] == "password"):
                        self.result_password = splitted_line[1].rstrip('\n')        
                    elif(splitted_line[0] == "db_name"):
                        self.db_name = splitted_line[1].rstrip('\n')                
        except EnvironmentError:            
            # irss_connection_info.ini 파일이 없음
            print("No IRSS DB Connection INI file.")
            use_default = 1
        
        if(use_default):
            self.__write_log_into_file("Reset to default IRSS DB Access configuration")
            self.result_hostname = ""
            self.result_portnumber = 3307
            self.result_username = ""
            self.result_password = ""
            self.db_name = "irss_db"

    # ============================================================================
    # 컨트롤에 입력된 값을 읽어서 클래스 멤버 변수에 저장하는 함수
    def __updateKcaConnParameterFromUI(self) -> int:
        try:
            res_year_from = int(self.cont_entry_year_from.get())
        except:
            self.__updateStatusBar(self.statusbar2, "오류 : 연도 문자열이 숫자가 아님")
            return 0

        now = datetime.now()
        self.res_year_to = now.year

        if(res_year_from > self.res_year_to):
            self.__updateStatusBar(self.statusbar2, "연도 범위 오류")
            return 0
        if(res_year_from < 2000):
            self.__updateStatusBar(self.statusbar2, "범위는 2000년도 이상으로 제한합니다.")
            return 0

        self.res_year_from = res_year_from        

        self.res_spectrummap_web_url = self.cont_entry_web_url.get()
        self.res_access_token_string = self.cont_entry_access_token.get()

        # 지역명 : 문자열을 콤마로 분리하여 리스트화
        self.area_name_string = self.cont_entry_area_list.get()
        self.res_area_name_list = self.area_name_string.split(',')

        # 체크박스들 : 체크되어 있으면 대응되는 키를 리스트에 추가        
        self.res_serv_prov_list = []
        self.res_serv_type_list = []
        self.res_bs_type_list = []
        for idx, check_var in enumerate(self.res_serv_prov_checkbox_var_list):
            if(check_var.get()):
                self.res_serv_prov_list.append(self.res_serv_prov_checkbox_key_list[idx])
        for idx, check_var in enumerate(self.res_serv_type_checkbox_var_list):
            if(check_var.get()):
                self.res_serv_type_list.append(self.res_serv_type_checkbox_key_list[idx])
        for idx, check_var in enumerate(self.res_bs_type_checkbox_var_list):
            if(check_var.get()):
                self.res_bs_type_list.append(self.res_bs_type_checkbox_key_list[idx]) 

        # HTTP Timeout
        try:
            self.http_timeout = int(self.cont_entry_http_timeout.get())

            # 숫자이지만 값이 10초 미만인경우 10초로 설정
            if(self.http_timeout < 10):
                self.cont_entry_http_timeout.delete(0, "end")
                self.cont_entry_http_timeout.insert(0, "10")
                self.http_timeout = 10

        except:
            # 숫자가 아닌 경우
            self.cont_entry_http_timeout.delete(0, "end")
            self.cont_entry_http_timeout.insert(0, "30")
            self.http_timeout = 30
            print("HTTP Timeout 입력값 오류. default로 복구 (30초)")

        # HTTP 재시도횟수
        try:
            self.http_num_retry = int(self.cont_entry_num_retry.get())

            if(self.http_num_retry < 1):                
                self.cont_entry_num_retry.delete(0, "end")
                self.cont_entry_num_retry.insert(0, "3")    
                self.http_num_retry = 3
        except:
            self.cont_entry_num_retry.delete(0, "end")
            self.cont_entry_num_retry.insert(0, "3")
            self.http_num_retry = 3
            print("HTTP 재시도 횟수 입력값 오류. default로 복구 (3회)")

    def __updateIrssDBConnInputFromUI(self) -> bool:
        self.result_hostname = self.cont_entry_irssdb_hostname.get()
        try:
            self.result_portnumber = int(self.cont_entry_irssdb_portnumber.get())
        except:
            self.__updateStatusBar(self.statusbar1, "DB 접속 포트번호 형식 오류")
            return False
        self.result_username = self.cont_entry_irssdb_username.get()
        self.result_password = self.cont_entry_irssdb_password.get()
        self.db_name = self.cont_entry_irss_db_name.get()
        return True

    def __writeIrssDBConnDefaultInfoIniFile(self) -> int:
        try:
            with open(self.filename_irss_db_conn_ini, "w") as conn_ini_file:
                out_str = ["hostname:"+self.result_hostname+"\n", \
                            "port_number:"+str(self.result_portnumber)+"\n", \
                            "username:"+self.result_username+"\n", \
                            "password:"+self.result_password+"\n", \
                            "db_name:"+self.db_name+"\n"]
                conn_ini_file.writelines(out_str)                
            return 1
        except EnvironmentError:
            return 0

    # ============================================================================
    # 클래스 멤버 변수에 저장된 값을 ini파일로 저장하는 함수
    # 이 함수 호출 전에 가능하면 updateParameterFromUI() 호출할 것
    def __writeKcaConnDefaultInfoIniFile(self) -> int:
        try:
            with open(self.filename_kca_conn_ini, "w") as conn_ini_file:
                serv_prov_str = ""
                serv_type_str = ""
                bs_type_str = ""
                for idx, serv_prov in enumerate(self.res_serv_prov_list):
                    if(idx > 0):
                        serv_prov_str = serv_prov_str + ","    
                    serv_prov_str = serv_prov_str + serv_prov
                for idx, element in enumerate(self.res_serv_type_list):
                    if(idx > 0):
                        serv_type_str = serv_type_str + ","    
                    serv_type_str = serv_type_str + element
                for idx, element in enumerate(self.res_bs_type_list):
                    if(idx > 0):
                        bs_type_str = bs_type_str + ","    
                    bs_type_str = bs_type_str + element

                out_str = [self.res_spectrummap_web_url+"\n", \
                            self.res_access_token_string+"\n", \
                            self.area_name_string+"\n", \
                            str(self.res_year_from)+"\n", \
                            str(self.res_year_to)+"\n", \
                            serv_prov_str+"\n", \
                            serv_type_str+"\n", \
                            bs_type_str+"\n"]

                print(out_str)
                conn_ini_file.writelines(out_str)                
            return 1
        except EnvironmentError:
            return 0

    def __updateStatusBar(self, status_bar:tkinter.Entry, line:str=""):
        try:
            status_bar["state"] = 'normal'
            status_bar.delete(0, "end")
            status_bar.insert(0, line)        
            status_bar["state"] = 'readonly'
            self.root.update()
        except:
            pass

    def __updateAllStatusBar(self, line1:str="", line2:str="", line3:str="", line4:str=""):
        statusbar_list = [self.statusbar1, self.statusbar2, self.statusbar3, self.statusbar4]
        line_list = [line1, line2, line3, line4]        
        try:
            for idx, statusbar in enumerate(statusbar_list):
                statusbar["state"] = 'normal'
                statusbar.delete(0, "end")
                statusbar.insert(0, line_list[idx])
                statusbar["state"] = 'readonly'
            self.root.update()
        except:
            pass

    def __IrssDBConnection_Setup(self, is_with_db_name:bool=True) -> bool:
        result = self.__updateIrssDBConnInputFromUI()
        if(result == False):
            return False          

        self.irss_db_manager.set_connection_info(self.result_hostname, self.result_portnumber, \
                                                self.result_username, self.result_password, self.db_name)

        if(is_with_db_name):
            if(self.irss_db_manager.connect() == False):
                return False
        else:
            if(self.irss_db_manager.connect(is_declare_db_name=False) == False):
                return False
        
        return True

    def __KcaOriginalDBConnection_Setup(self, is_with_db_name:bool=True) -> bool:
        result = self.__updateKcaConnParameterFromUI()
        if(result == 0):
            return False       

        self.kca_originaldatadb_manager.set_connection_info(self.result_hostname, self.result_portnumber, \
                                                            self.result_username, self.result_password, self.db_name)

        if(is_with_db_name):
            if(self.kca_originaldatadb_manager.connect() == False):
                return False
        else:
            if(self.kca_originaldatadb_manager.connect(is_declare_db_name=False) == False):
                return False

        return True

    def __IrssDBConnection_Close(self):
        self.irss_db_manager.close_connection()

    def __KcaOriginalDBConnection_Close(self):
        self.kca_originaldatadb_manager.close_db_connection()

    def __buttonDisplay_SwitchToNormal(self, target_cancel_btn_index):
        # 취소버튼 숨기기
        if(target_cancel_btn_index == 0):
            self.btnCancelDBUpdate["state"] = "disabled"
            self.btnCancelDBUpdate._place_info = self.btnCancelDBUpdate.place_info()
            self.btnCancelDBUpdate.place_forget()
        elif(target_cancel_btn_index == 1):
            self.btnCancelHTZ["state"] = "disabled"
            self.btnCancelHTZ._place_info = self.btnCancelHTZ.place_info()
            self.btnCancelHTZ.place_forget()        

        # 다른 버튼 되돌리기
        self.btnSave["state"] = "normal"
        self.btnStartDBUpdate.place(**self.btnStartDBUpdate._place_info)
        self.btnStartHTZ.place(**self.btnStartHTZ._place_info)
        self.btnCheckHTZ.place(**self.btnCheckHTZ._place_info)
        self.btnDBManagement.place(**self.btnDBManagement._place_info)
        self.btnDBTableCreate.place(**self.btnDBTableCreate._place_info)
        self.btnDBTableEmpty.place(**self.btnDBTableEmpty._place_info)
        self.btnCreateFoliumHtmlMap.place(**self.btnCreateFoliumHtmlMap._place_info)
        self.btnTimerTest.place(**self.btnTimerTest._place_info)

        self.root.update()

    def __buttonDisplay_SwitchToCancel(self, target_cancel_btn_index):
        # 취소버튼 보이기
        if(target_cancel_btn_index == 0):
            self.btnCancelDBUpdate["state"] = "normal"
            self.btnCancelDBUpdate.place(**self.btnCancelDBUpdate._place_info)
        elif(target_cancel_btn_index == 1):
            self.btnCancelHTZ["state"] = "normal"
            self.btnCancelHTZ.place(**self.btnCancelHTZ._place_info)

        # 동작버튼 숨기기
        self.btnSave["state"] = "disabled"
        self.btnStartDBUpdate._place_info = self.btnStartDBUpdate.place_info()
        self.btnStartDBUpdate.place_forget()
        self.btnStartHTZ._place_info = self.btnStartHTZ.place_info()
        self.btnStartHTZ.place_forget()        
        self.btnCheckHTZ._place_info = self.btnCheckHTZ.place_info()
        self.btnCheckHTZ.place_forget()  
        self.btnDBManagement._place_info = self.btnDBManagement.place_info()
        self.btnDBManagement.place_forget()
        self.btnDBTableCreate._place_info = self.btnDBTableCreate.place_info()
        self.btnDBTableCreate.place_forget()
        self.btnDBTableEmpty._place_info = self.btnDBTableEmpty.place_info()
        self.btnDBTableEmpty.place_forget()
        self.btnCreateFoliumHtmlMap._place_info = self.btnCreateFoliumHtmlMap.place_info()
        self.btnCreateFoliumHtmlMap.place_forget()        
        self.btnTimerTest._place_info = self.btnTimerTest.place_info()
        self.btnTimerTest.place_forget()
        self.root.update()

    # DB 관리 기능 버튼
    def __eventDBManagementButton(self):
        if(self.btnDBTableCreate['state'] == 'disabled'):
            self.btnDBTableCreate['state'] = 'normal'
            self.btnDBTableEmpty['state'] = 'normal'
            self.btnDBManagement['text'] = "DB 관리기능 끄기"
        else:
            self.btnDBTableCreate['state'] = 'disabled'
            self.btnDBTableEmpty['state'] = 'disabled'
            self.btnDBManagement['text'] = "DB 관리기능 활성화"
        return

    def __eventCreateDBTableButton(self):
        if(self.__IrssDBConnection_Setup(False) == False):
            self.__updateAllStatusBar("DB 연결 실패", "", "", "") 
            return
        if(self.__KcaOriginalDBConnection_Setup(False) == False):
            self.__updateAllStatusBar("DB 연결 실패", "", "", "") 
            return

        self.kca_originaldatadb_manager.initialize_db_table_if_not_exists()        

        for service_provider in self.res_serv_prov_checkbox_key_list:
            for service_type in self.res_serv_type_checkbox_key_list:
                scenario_table_name = service_provider + "_" + service_type
                self.irss_db_manager.create_db_table_tbl(scenario_table_name)

        self.__updateAllStatusBar("DB 테이블 생성 실행 완료", "", "", "")
        self.__write_log_into_file("DB 테이블 생성 실행 완료")

        self.__IrssDBConnection_Close()
        self.__KcaOriginalDBConnection_Close()

    def __eventEmptyDBTableButton(self):        
        if(self.__IrssDBConnection_Setup() == False):
            self.__updateAllStatusBar("DB 연결 실패", "", "", "") 
            return
        if(self.__KcaOriginalDBConnection_Setup() == False):
            self.__updateAllStatusBar("DB 연결 실패", "", "", "") 
            return

        self.irss_db_manager.do_truncate_all_table(self.res_serv_prov_checkbox_key_list, self.res_serv_type_checkbox_key_list)
        self.kca_originaldatadb_manager.do_truncate_all_table()
        self.__updateAllStatusBar("모든 DB 테이블 비우기 완료", "", "", "")
        self.__write_log_into_file("모든 DB 테이블 비우기 완료")

        self.__IrssDBConnection_Close()
        self.__KcaOriginalDBConnection_Close()

    # ================================================================================
    # 버튼 : 정지하기 (정지 플래그 설정. 정지 후 동작은 해당 버튼에서 수행)
    # ================================================================================
    def __eventStopButton(self):              # 버튼 : 정지하기. 정지 후처리는 시작버튼에서 처리 필요
        self.stop_button_pressed = 1

    # ================================================================================
    # 버튼 : 저장하기
    # ================================================================================
    def __eventSaveButton(self):              
        self.__updateAllStatusBar("", "", "", "")
        self.__updateStatusBar(self.statusbar1, "입력값 저장하기")

        # IRSS 연결 파라메터 읽어서 저장
        result = self.__updateIrssDBConnInputFromUI()
        if(result == False):
            self.__updateStatusBar(self.statusbar2, "저장 실패. DB 연결을 위한 입력값에 오류가 있습니다.")
            return
        result = self.__writeIrssDBConnDefaultInfoIniFile()
        if(result == 1):
            self.__updateStatusBar(self.statusbar2, "저장 완료 (%s)" % (self.filename_irss_db_conn_ini) )
        else:
            self.__updateStatusBar(self.statusbar2, "저장 실패. %s 쓰기권한 확인 필요" % (self.filename_irss_db_conn_ini))
        

        # KCA 연결 파라메터 읽어서 저장        
        result = self.__updateKcaConnParameterFromUI()               # 입력 UI에서 읽어오기
        if(result == 0):
            self.__updateStatusBar(self.statusbar3, "저장 실패. KCA 연결을 위한 입력값에 오류가 있습니다.")
            return
        result = self.__writeKcaConnDefaultInfoIniFile()             # 파일에 쓰기
        if(result == 1):
            self.__updateStatusBar(self.statusbar3, "저장 완료 (%s)" % (self.filename_kca_conn_ini))
        else:
            self.__updateStatusBar(self.statusbar3, "저장 실패. %s 쓰기권한 확인 필요" % (self.filename_kca_conn_ini))


    # ================================================================================
    # 버튼 : KCA 웹조회 및 DB 갱신 버튼
    # ================================================================================
    def __eventStartDBUpdateButton(self):
        self.job_is_ongoing = 1

        self.btnStartDBUpdate['bg'] = '#888888'
        self.__updateAllStatusBar("", "", "", "")    

        # DB 연결 시도
        result = self.__KcaOriginalDBConnection_Setup()        
        if(result == False):
            self.__updateStatusBar(self.statusbar1, "DB 연결 실패 : KCA 원본 대조 DB 테이블")
            self.__write_log_into_file("DB 연결 실패 : KCA 원본 대조 DB 테이블")
            return
        result = self.__IrssDBConnection_Setup()
        if(result == False):
            self.__updateStatusBar(self.statusbar1, "DB 연결 실패 : HTZ 분석 DB 테이블")
            self.__write_log_into_file("DB 연결 실패 : HTZ 분석 DB 테이블")
            return

        # 연결 성공시 해당 설정을 저장
        self.__writeIrssDBConnDefaultInfoIniFile()

        # KCA Connection Manager에 KCA 연결 정보 설정
        self.kca_conn_manager.set_spectrummap_site_url(self.res_spectrummap_web_url)
        self.kca_conn_manager.set_service_provider_list(self.res_serv_prov_list)
        self.kca_conn_manager.set_service_type_list(self.res_serv_type_list)
        self.kca_conn_manager.set_access_token(self.res_access_token_string)
        self.kca_conn_manager.set_header_cookie("")
        target_year_list = []
        for year in range(self.res_year_from, self.res_year_to+1):      # 연도 목록 구성. 종료도 포함시켜야하므로 +1
            target_year_list.append(year)

        # 버튼 활성화/비활성화를 변경
        self.__buttonDisplay_SwitchToCancel(0)

        # Job 목록을 구성
        job_list = []
        for area_name in self.res_area_name_list:
            for bs_type in self.res_bs_type_list: 
                for service_provider_name in self.res_serv_prov_list:
                    for service_type in self.res_serv_type_list:
                        for year in target_year_list:
                            job_entry = {'area':area_name, 'bs_type':bs_type, 'serv_provider':service_provider_name, \
                                        'serv_type':service_type, 'year':year}

                            job_list.append(job_entry)

        number_of_jobs = len(job_list)
        self.stop_button_pressed = 0  
        stop_signalled = False
        stop_reason_button_pressed = False
        stop_reason_error = False
        max_pindex = 10

        # Job 목록에 따라 조회작업 시작
        RDS_STA_CD_list = ["00"]           # 활성화 기지국만 조회
        for idx, job_entry in enumerate(job_list):
            if(stop_signalled):
                break

            area_name = job_entry['area']
            bs_type = job_entry['bs_type']
            service_provider_name = job_entry['serv_provider']
            service_type = job_entry['serv_type']
            year = job_entry['year']

            for rds_sta_cd in RDS_STA_CD_list:                          # 활성화/비활성화
                if(stop_signalled):
                    break
                
                request_count_str = "%d/%d" % ((idx+1), len(job_list))
                request_set_str =  "%s+%s+%d+%s+%s+%s" % (rds_sta_cd, area_name, year, service_provider_name, service_type, bs_type)
                self.__updateStatusBar(self.statusbar1, "조회" + request_count_str + " : " + request_set_str)                            

                for index in range (1, max_pindex+1):                                        # pIndex                                
                    # 중단 버튼이 눌렸으면 정지
                    if(self.stop_button_pressed):
                        stop_signalled = 1
                        stop_reason_button_pressed = 1
                        break

                    # 1) KCA에 OPEN API로 요청 날려서 JSON 문자열 획득
                    # print(area_name, year, service_provider_name, service_type, bs_type, index)
                    self.__write_log_into_file("KCA 웹서버 접속 및 조회 요청 : " + request_set_str)
                    json_text = self.kca_conn_manager.get_jsontext_for_area_from_web(rds_sta_cd, \
                                    int(bs_type), service_type, service_provider_name, area_name, year, index, \
                                    self.http_timeout, self.http_num_retry)                                    

                    if(json_text == None):
                        self.__write_log_into_file("HTTP Timeout. KCA 웹서버 접속 실패")
                        self.__updateStatusBar(self.statusbar2, "HTTP Timeout. KCA 웹서버 접속 실패")
                        stop_signalled = 1
                        stop_reason_error = 1
                        break

                    # 2) JSON 형식 문자열 --> JSON 개체로 변경
                    try:
                        json_object = json.loads(json_text)
                    except json.JSONDecodeError as json_error:
                        self.__write_log_into_file("수신 JSON 디코딩 에러 : " + request_set_str)
                        print(json_error.msg)

                        # 받은 텍스트 덤프
                        with open(request_set_str + "_errored.json", 'w') as json_dump:
                            json_dump.write(json_text)
                                                                
                        stop_signalled = 1
                        stop_reason_error = 1


                    # 3) 요청 결과 상태 확인 (JSON 개체의 RESULT_CODE 부분 확인)
                    result_code = self.kca_conn_manager.get_result_code_from_kca_json_object(json_object)
                    stop_signalled, is_next_iteration, result_code_message = self.kca_conn_manager.analysis_result_code(result_code)
                    if(result_code == None):
                        result_code_message = "Json 개체 획득 실패"
                        self.__write_log_into_file(" -- Json 개체 획득 실패")
                    else:
                        self.__write_log_into_file(" -- ResultCode : " + result_code)

                    self.__updateStatusBar(self.statusbar2, "[%s 페이지:%d] 수신, ResultCode : %s" % (request_set_str, index, result_code))   
                    self.__updateStatusBar(self.statusbar3, "%s" % (result_code_message))

                    if(is_next_iteration):
                        sleep(1)                           # 다음 것을 빨리 요청하지 않기 위해 1초 휴식
                        break
                    
                    if(stop_signalled):
                        stop_reason_error = 1
                        break

                    # Optional) 다운 받은 것을 JSON 파일로 저장
                    """
                    outfile_name = str(area_name) + str(year) + str(service_provider_name) \
                        + str(service_type) + str(bs_type) + "_" + str(index) + ".json"

                    with open(outfile_name, 'w') as outfile:
                        print("JSON Dump : %s" % (outfile_name))
                        json.dump(json_text, outfile)
                    """

                    # 4) KCA에서 받은 JSON의 RESULT 부분을 확인하여 각 entry에 대해 작업 수행
                    kca_json_entry_array = json_object.get("RESULT")
        
                    if (kca_json_entry_array == None):
                        self.__updateStatusBar(self.statusbar1, "JSON 개체 중 RESULT 부분 분석에 실패하였습니다.")
                        self.__write_log_into_file("JSON 개체 중 RESULT 부분 분석에 실패하였습니다.")
                        break
                    
                    for kca_json_entry in kca_json_entry_array:
                        # 4-1) json format --> KCA 원본 DB 상 Column 순서대로의 list 획득
                        entry_read_list = self.kca_originaldatadb_manager.create_parsed_list_from_kca_json_entry(kca_json_entry)

                        # 4-2) 해당 항목을 분석하여 취해야 할 조치를 확인                                        
                        kca_orig_db_job, htz_db_job = self.kca_originaldatadb_manager.decide_job_from_parsed_entry_list(entry_read_list)

                        # 4-3) 리턴 코드에 따른 KCA 원본 DB 조치
                        if(kca_orig_db_job == 1):
                            # 추가
                            self.__write_log_into_file("KCA 원본 DB 기지국 추가 : " + entry_read_list[0])
                            self.kca_originaldatadb_manager.insert_to_db_from_parsed_entry_list(entry_read_list, service_provider_name)
                        elif(kca_orig_db_job == 2 or kca_orig_db_job == 3):
                            # 변경
                            self.__write_log_into_file("KCA 원본 DB 기지국 갱신: " + entry_read_list[0])
                            self.kca_originaldatadb_manager.update_to_db_from_parsed_entry_list(entry_read_list, service_provider_name)
                        else:
                            pass                                            

                        # 4-4) 리턴 코드에 따른 HTZ 입력 DB 조치
                        if(htz_db_job == 0):           
                            # 4-4-1) 분석 필요 없음
                            pass
                        elif(htz_db_job == 1 or htz_db_job == 2):         
                            # 4-4-2) HTZ 분석이 필요함 (신규(1) or 기지국 무효->유효로 업데이트(2))
                            # HTZ 요청을 위한 DB에 추가                                            
                            target_base_table_name = service_provider_name + "_" + service_type
                            self.__write_log_into_file("HTZ 분석 DB 추가 : 기지국 " + entry_read_list[0] + " / DB 대상 : " + target_base_table_name)
                            self.irss_db_manager.insert_kca_json_entry_into_update_req_table_v2(target_base_table_name, kca_json_entry, service_provider_name)
                            pass
                        else:                           
                            # 4-4-3) 기존 HTZ 분석 결과 삭제 필요 (기지국 유효->무효로 업데이트)
                            #       일단 DB에서 사라진 경우는 배제하자. (방금 조회한 전체에 대한 DB 구성 후 비교 작업 필요)

                            # TODO : 현재는 아무 조치하지 않음. 기존 HTZ 분석결과 테이블 뒤져서 삭제/비활성화 조치필요시 여기에 코드 삽입

                            pass 

                    # GUI 업데이트 : 메시지 표시 갱신 및 사용자의 취소버튼 입력 받기
                    self.root.update()
                # == end for index in range (1, max_pindex): ======================================
            # == end for rds_sta_cd in ... ========================================================

            task_complete_message = "작업완료 : %d/%d" % (idx+1, number_of_jobs)
            self.__write_log_into_file(task_complete_message)
            self.__updateStatusBar(self.statusbar4, task_complete_message)   
            print(task_complete_message)

            # GUI 업데이트 : 메시지 표시 갱신 및 사용자의 취소버튼 입력 받기
            self.root.update()
        # == end for job_entry in ... ============================================================

        # 버튼 활성화 여부 되돌리기
        self.__buttonDisplay_SwitchToNormal(0)
        self.btnStartDBUpdate['bg'] = '#99eeff'

        # 메시지 표시. Statusbar 2번에는 오류메시지가 있으므로 남기기
        if(stop_reason_button_pressed):
            self.__updateStatusBar(self.statusbar1, "사용자에 의해 작업이 중지되었습니다")
            self.__updateStatusBar(self.statusbar4, "")
        elif(stop_reason_error):
            self.__updateStatusBar(self.statusbar1, "오류가 발생하여 작업이 중단되었습니다.")        
        else:
            self.__updateAllStatusBar("모든 작업이 완료되었습니다.", "", "", "")

        # DB 연결 끊기
        self.__IrssDBConnection_Close()
        self.__KcaOriginalDBConnection_Close()   

        self.job_is_ongoing = 0   

    # ================================================================================
    # 버튼 : HTZ 동작필요성 체크 버튼
    # ================================================================================
    def __eventCheckHTZButton(self):
        self.__updateAllStatusBar("", "", "", "")

        self.__updateIrssDBConnInputFromUI()
        self.__updateKcaConnParameterFromUI()

        # DB 연결 시도
        result = self.__IrssDBConnection_Setup()
        if(result == False):
            self.__updateStatusBar(self.statusbar1, "DB 연결 실패")
            return

        # 연결 성공시 해당 설정을 저장
        self.__writeIrssDBConnDefaultInfoIniFile()

        list_update_required_tbl = []
        for service_provider_name in self.res_serv_prov_list:                   # 서비스 제공자
            for service_type in self.res_serv_type_list:                        # 서비스 유형 (2G, ...)
                base_table_name = service_provider_name + "_" + service_type  
                num_rows_in_table = self.irss_db_manager.get_num_of_rows_in_update_req_table(base_table_name)
                if(num_rows_in_table > 0): 
                     list_update_required_tbl.append(base_table_name + "(%d개)" % (num_rows_in_table))

        str_table_list = ""
        for entry in list_update_required_tbl:
            str_table_list = str_table_list + entry + "/"

        self.__updateStatusBar(self.statusbar1, "분석 업데이트 필요 : %d 개" % (len(list_update_required_tbl)))
        self.__updateStatusBar(self.statusbar2, str_table_list)

        # DB 연결 끊기
        self.__IrssDBConnection_Close()

    # ================================================================================
    # 버튼 : HTZ 동작시키기 버튼
    # ================================================================================
    def __eventStartHTZButton(self):
        self.__write_log_into_file(" **** HTZ 분석 요청 시작 **** ")

        stop_signalled = 0
        self.job_is_ongoing = 1
        self.stop_button_pressed = 0

        # 취소버튼 보이고, 다른 버튼 숨기기
        self.__buttonDisplay_SwitchToCancel(1)

        # TODO : 각 [기지국]_[기술] DB에 대해 HTZ 분석 배치파일 실행하기
        workingDir = os.curdir

        self.__updateAllStatusBar("", "", "", "")    

        # DB 연결에 사용할 입력값 읽어오기
        result = self.__updateKcaConnParameterFromUI()              # KCA 관련 입력값 업데이트. (KCA 원본 DB 연결하지 않아서 별도 처리)
        if(result == False):
            self.__updateStatusBar(self.statusbar1, "입력 정보 오류")
            return        

        for service_provider_name in self.res_serv_prov_list:                   # 서비스 제공자
            if(stop_signalled):
                break
            for service_type in self.res_serv_type_list:                        # 서비스 유형 (2G, ...)
                if(self.stop_button_pressed):
                    stop_signalled = 1
                    break

                # HTZ DB 접속.
                # HTZ 분석이 오래 걸려서 SQL 접속이 끊어지는 문제 해결 위해서 루프 단위로 접속을 시도
                result = self.__IrssDBConnection_Setup()                    
                if(result == False):
                    self.__updateStatusBar(self.statusbar1, "DB 연결 실패")
                    return

                # 연결 성공시 해당 설정을 저장
                self.__writeIrssDBConnDefaultInfoIniFile()

                self.__updateStatusBar(self.statusbar1, "HTZ 실행대상 : %s_%s" % (service_provider_name, service_type))
                base_table_name = service_provider_name + "_" + service_type                         

                # 업데이트 필요 DB가 비어있는지 확인
                num_rows_in_table = self.irss_db_manager.get_num_of_rows_in_update_req_table(base_table_name)

                # DB 연결 미리 끊기
                # 배치파일 실행이 오래 걸리므로 SQL 연결이 끊어지는 경우가 있어서 SQL 연결을 끊고 배치파일을 실행할 필요 있음
                self.__IrssDBConnection_Close() 

                if(num_rows_in_table > 0):         
                    batch_file_name = service_provider_name + "-" + service_type + ".bat"
                    self.__updateStatusBar(self.statusbar2, "%s 실행" % (batch_file_name))

                    self.__write_log_into_file("배치파일 실행 : " + batch_file_name)
                    # os.system(batch_file_name)
                    try:
                        subprocess.run(batch_file_name)
                    except:
                        self.__write_log_into_file("*** 배치파일 (%s) 찾기 실패. 실행 불가." % (batch_file_name), display_to_stdout=True)
                        continue

                    self.__write_log_into_file("실행완료 : " + batch_file_name)
                    self.__write_log_into_file(" == DB 이동 시작 (%s) =======================" % (batch_file_name) )

                    # 배치파일 실행이 완료되면 다시 HTZ DB 접속
                    result = self.__IrssDBConnection_Setup()                    
                    if(result == False):
                        self.__updateStatusBar(self.statusbar1, "배치파일 실행 완료후 DB 연결 실패")
                        return

                    included_list, excluded_list = self.irss_db_manager.overwrite_update_req_table_into_complete_table(base_table_name)

                    for info1 in included_list:
                        self.__write_log_into_file("  HTZ 분석 완료 확인 : " + info1)
                    for info1 in excluded_list:
                        self.__write_log_into_file("  *** HTZ 분석되지 않음 : " + info1)

                    self.__write_log_into_file(" == DB 이동 완료  (%s)=======================================" % (batch_file_name))

                    # DB 옮기기 작업 완료. 연결 끊기.
                    self.__IrssDBConnection_Close()                     
                else:
                    self.__write_log_into_file("입력 테이블 비어있음. 작업 생략. 식별자 정보 : " + base_table_name, display_to_stdout=True)                                                   
            # end for service_type in self.res_serv_type_list: ==================
        # end for service_provider_name in self.res_serv_prov_list: ===============

        self.__write_log_into_file("작업 완료")
        self.__updateStatusBar(self.statusbar3, "작업 완료")        

        # 취소버튼 숨기고, 버튼 복구
        self.__buttonDisplay_SwitchToNormal(1)

        self.job_is_ongoing = 0

    def __onTimerTest(self):
        now = datetime.now()

        if(self.timer_is_on):
            # self.__eventStartDBUpdateButton()
            # self.__eventCheckHTZButton()

            self.timer = threading.Timer(self.__timer_interval_sec, self.__onTimerTest)
            self.timer.start()
            message_str = "타이머에 의한 실행 완료 : " + str(now) + ". 60초 후 재실행"
            self.__updateStatusBar(self.statusbar4, message_str)


    def __eventToggleTimerButton(self):
        if(self.timer_is_on == 0):
            self.timer_is_on = 1
            self.__onTimerTest()
        else:
            self.timer_is_on = 0
            self.timer.cancel()
            self.__updateStatusBar(self.statusbar4, "타이머 정지")

    def __eventMapButton(self):
        result = self.__KcaOriginalDBConnection_Setup()
        if(result == False):
            self.__updateStatusBar(self.statusbar1, "DB 연결 실패")
            return

        self.__updateKcaConnParameterFromUI()

        # 사업자-기술 별 지도
        for service_provider_name in self.res_serv_prov_list:
            for service_type in self.res_serv_type_list:
                self.kca_originaldatadb_manager.create_bs_location_map(service_provider_name, service_type)

        # 전체 기지국 지도
        self.kca_originaldatadb_manager.create_bs_location_map("", "")

        self.__KcaOriginalDBConnection_Close()            

    # ===================================================================================================================================
    # ===================================================================================================================================
    # 입력창을 띄우고 사용자 입력을 대기
    def __createLabelAndEntryControl(self, label_x, entry_x, y, entry_width, entry_height, label_text, entry_text) -> tkinter.Entry:
        tkinter.Label(self.root, text=label_text, justify='left').place(x=label_x, y=y)
        entry_control = tkinter.Entry(self.root)
        entry_control.place(x=entry_x, y=y, width=entry_width, height=entry_height)
        entry_control.insert(0, entry_text)

        return entry_control        

    def __make_irss_db_connection_ui(self):
        x_base = 20
        x_entry = x_base + 150
        y_base = 20
        y_step = 30
        entry_width = 100
        entry_height = 20
        
        tkinter.Label(self.root, text="[IRSS DB 연결설정]", justify='left').place(x=x_base, y=y_base)

        idx = 1
        new_y = y_base + y_step*idx
        self.cont_entry_irssdb_hostname = self.__createLabelAndEntryControl(x_base, x_entry, new_y, entry_width, entry_height, \
                                                                    "서버 IP 또는 호스트명 :", self.result_hostname)
        idx = 2
        new_y = y_base + y_step*idx
        self.cont_entry_irssdb_portnumber = self.__createLabelAndEntryControl(x_base, x_entry, new_y, entry_width, entry_height, \
                                                                    "포트번호 (1~65535) :", self.result_portnumber)
        idx = 3
        new_y = y_base + y_step*idx
        self.cont_entry_irssdb_username = self.__createLabelAndEntryControl(x_base, x_entry, new_y, entry_width, entry_height, \
                                                                    "사용자명 :", self.result_username)
        idx = 4
        new_y = y_base + y_step*idx
        self.cont_entry_irssdb_password = self.__createLabelAndEntryControl(x_base, x_entry, new_y, entry_width, entry_height, \
                                                                    "암호 :", self.result_password)

        idx = 5
        new_y = y_base + y_step*idx
        self.cont_entry_irss_db_name = self.__createLabelAndEntryControl(x_base, x_entry, new_y, entry_width, entry_height, \
                                                                    "Database 이름 :", self.db_name)

    def __make_kca_connection_ui(self):
        base_x = 300
        base_width = 300
        x_step = 150
        base_y=20       
        base_height = 20
        y_step = 30

        # 웹주소 입력부
        idx = 0
        new_y = base_y + y_step*idx
        self.cont_entry_web_url = self.__createLabelAndEntryControl(base_x, base_x+x_step, new_y, base_width, base_height, \
                                                                    "웹 주소 :", self.res_spectrummap_web_url)                                                                    
        # 인증키 입력부                                                                    
        idx = 1
        new_y = base_y + y_step*idx
        self.cont_entry_access_token = self.__createLabelAndEntryControl(base_x, base_x+x_step, new_y, base_width, base_height, \
                                                                    "전파누리 접근키(key) :", self.res_access_token_string)   
        # 지역 목록 입력부
        area_name_list_str = ""        
        area_name_cnt = 0
        for area_name in self.res_area_name_list:            
            if(area_name_cnt > 0):
                area_name_list_str = area_name_list_str + ","
            area_name_list_str = area_name_list_str + area_name            
            area_name_cnt = area_name_cnt + 1

        idx = 2
        new_y = base_y + y_step*idx                                                            
        self.cont_entry_area_list = self.__createLabelAndEntryControl(base_x, base_x+x_step, new_y, base_width, base_height, \
                                                                    "검색 지역 목록 :", area_name_list_str)  
        tkinter.Label(self.root, text="( 지역이 여러개일 경우 콤마(,)로 구분 )", justify='left').place(x=base_x+x_step, y=new_y+y_step)                

        # 연도 입력부
        idx = 4
        new_y = base_y + y_step*idx  
        year_width = 50
        tkinter.Label(self.root, text="검색 대상 연도 : ", justify='left').place(x=base_x, y=new_y)
        tkinter.Label(self.root, text="시작", justify='left').place(x=base_x+x_step, y=new_y)
        self.cont_entry_year_from = tkinter.Entry(self.root)
        self.cont_entry_year_from.place(x=base_x+x_step+50, y=new_y, width=year_width, height=base_height)
        self.cont_entry_year_from.insert(0, str(self.res_year_from))

        # 시설자, 서비스 - 체크박스 처리
        idx = 5
        new_y = base_y + y_step*idx
        tkinter.Label(self.root, text="조회 대상 시설자 : ", justify='left').place(x=base_x, y=new_y)
        self.cont_checkbox_serv_prov_sk = tkinter.Checkbutton(text="SK", variable=self.res_serv_prov_sk)
        self.cont_checkbox_serv_prov_sk.place(x=base_x+x_step, y=new_y)
        self.cont_checkbox_serv_prov_kt = tkinter.Checkbutton(text="KT", variable=self.res_serv_prov_kt)
        self.cont_checkbox_serv_prov_kt.place(x=base_x+x_step+80, y=new_y)
        self.cont_checkbox_serv_prov_lg = tkinter.Checkbutton(text="LG", variable=self.res_serv_prov_lg)
        self.cont_checkbox_serv_prov_lg.place(x=base_x+x_step+160, y=new_y)

        idx = 6
        new_y = base_y + y_step*idx
        tkinter.Label(self.root, text="조회 대상 서비스 : ", justify='left').place(x=base_x, y=new_y)
        self.cont_checkbox_serv_type_2g = tkinter.Checkbutton(text="2G", variable=self.res_serv_type_2g)
        self.cont_checkbox_serv_type_2g.place(x=base_x+x_step, y=new_y)
        self.cont_checkbox_serv_type_3g = tkinter.Checkbutton(text="3G", variable=self.res_serv_type_3g)
        self.cont_checkbox_serv_type_3g.place(x=base_x+x_step+80, y=new_y)
        self.cont_checkbox_serv_type_4g = tkinter.Checkbutton(text="4G", variable=self.res_serv_type_4g)
        self.cont_checkbox_serv_type_4g.place(x=base_x+x_step+160, y=new_y)
        self.cont_checkbox_serv_type_5g = tkinter.Checkbutton(text="5G", variable=self.res_serv_type_5g)
        self.cont_checkbox_serv_type_5g.place(x=base_x+x_step+240, y=new_y)

        idx = 7
        new_y = base_y + y_step*idx
        tkinter.Label(self.root, text="조회 대상 국종 : ", justify='left').place(x=base_x, y=new_y)
        self.cont_checkbox_bstype1 = tkinter.Checkbutton(text="기지국(32)", variable=self.res_bs_type_32)
        self.cont_checkbox_bstype1.place(x=base_x+x_step, y=new_y)
        self.cont_checkbox_bstype2 = tkinter.Checkbutton(text="중계기(85)", variable=self.res_bs_type_85)
        self.cont_checkbox_bstype2.place(x=base_x+x_step+80, y=new_y)

        idx = 8
        new_y = base_y + y_step*idx
        http_label_width = 120
        http_entry_cont_width = 40
        self.http_timeout = 30
        self.http_num_retry = 3
        self.cont_entry_http_timeout = self.__createLabelAndEntryControl(base_x, base_x+http_label_width, new_y, http_entry_cont_width, base_height, \
                                                                    "HTTP Timeout (초) :", self.http_timeout)  
        self.cont_entry_num_retry = self.__createLabelAndEntryControl(10+base_x+http_label_width+http_entry_cont_width, base_x+2*http_label_width+http_entry_cont_width+10, \
                                                                    new_y, http_entry_cont_width, base_height, \
                                                                    "HTTP 재시도횟수 :", self.http_num_retry)  

        # 버튼 부분
        base_x = 20
        button_width_small = 100
        button_width_large = 200
        button_height = 40
        button_x_margin = 20

        idx = 9
        new_y = base_y + y_step*idx
        self.btnSave = tkinter.Button(self.root, text="설정값 저장", command=self.__eventSaveButton)        
        self.btnSave.place(x=base_x, y=new_y, width=button_width_small, height=button_height)

        # DB 갱신 버튼
        self.btnStartDBUpdate = tkinter.Button(self.root, text="HTZ 분석 DB 업데이트 시작", command=self.__eventStartDBUpdateButton, bg='#99eeff')
        new_x = base_x+button_width_small+button_x_margin
        self.btnStartDBUpdate.place(x=new_x, y=new_y, width=button_width_large, height=button_height)

        # 동일 위치에 취소버튼 만들고 숨기기
        self.btnCancelDBUpdate = tkinter.Button(self.root, text="작업 중단", command=self.__eventStopButton, state='disabled')
        self.btnCancelDBUpdate.place(x=new_x, y=new_y, width=button_width_large, height=button_height)
        self.btnCancelDBUpdate._place_info = self.btnCancelDBUpdate.place_info()
        self.btnCancelDBUpdate.place_forget()


        self.btnCheckHTZ = tkinter.Button(self.root, text="HTZ 분석 필요성 확인", command=self.__eventCheckHTZButton)
        new_x = base_x+button_width_small+button_x_margin + (button_width_large + button_x_margin)
        self.btnCheckHTZ.place(x=new_x, y=new_y, width=button_width_large, height=button_height)

        # HTZ 분석 버튼
        self.btnStartHTZ = tkinter.Button(self.root, text="HTZ 분석 시작", command=self.__eventStartHTZButton, bg='#99eeff')
        new_x = base_x+button_width_small+button_x_margin + 2*(button_width_large + button_x_margin)
        self.btnStartHTZ.place(x=new_x, y=new_y, width=button_width_large, height=button_height)

        # 동일 위치에 취소버튼 만들고 숨기기. 취소 메커니즘은 동일하므로 위 취소 버튼과 동일 함수 사용
        self.btnCancelHTZ = tkinter.Button(self.root, text="작업 중단", command=self.__eventStopButton, state='disabled')
        self.btnCancelHTZ.place(x=new_x, y=new_y, width=button_width_large, height=button_height)
        self.btnCancelHTZ._place_info = self.btnCancelHTZ.place_info()
        self.btnCancelHTZ.place_forget()    


        # 상태 표시줄
        idx = 11
        new_y = base_y + y_step*idx
        self.statusbar1 = tkinter.Entry(self.root, text="", state='readonly')
        self.statusbar1.place(x=base_x, y=new_y, width=self.window_width - 40, height=20)
        self.statusbar2 = tkinter.Entry(self.root, text="", state='readonly')
        self.statusbar2.place(x=base_x, y=new_y+20, width=self.window_width - 40, height=20)
        self.statusbar3 = tkinter.Entry(self.root, text="", state='readonly')
        self.statusbar3.place(x=base_x, y=new_y+40, width=self.window_width - 40, height=20)
        self.statusbar4 = tkinter.Entry(self.root, text="", state='readonly')
        self.statusbar4.place(x=base_x, y=new_y+60, width=self.window_width - 40, height=20)


        # 상태 표시줄 아래 임시 버튼들
        idx = 14
        new_y = base_y + y_step*idx
        self.btnCreateFoliumHtmlMap = tkinter.Button(self.root, text="KCA 데이터 DB → 지도 출력", command=self.__eventMapButton)
        self.btnCreateFoliumHtmlMap.place(x=base_x, y=new_y, width=button_width_large, height=button_height)
        self.btnTimerTest = tkinter.Button(self.root, text="타이머 함수 테스트", command=self.__eventToggleTimerButton)
        self.btnTimerTest.place(x=base_x + 2*(button_x_margin + button_width_large), y=new_y, width=button_width_large, height=button_height)
        
        idx = 17
        new_y = base_y + y_step*idx
        self.btnDBManagement = tkinter.Button(self.root, text="DB 관리 기능 활성화", command=self.__eventDBManagementButton)
        self.btnDBManagement.place(x=base_x, y=new_y, width=button_width_large, height=button_height)
        self.btnDBTableCreate = tkinter.Button(self.root, text="DB 및 테이블 생성 (임시/주의)", command=self.__eventCreateDBTableButton, state='disabled')
        self.btnDBTableCreate.place(x=base_x+1*(button_width_large+button_x_margin), y=new_y, width=button_width_large, height=button_height)        
        self.btnDBTableEmpty = tkinter.Button(self.root, text="테이블 내용 비우기 (임시/주의)", command=self.__eventEmptyDBTableButton, state='disabled')
        self.btnDBTableEmpty.place(x=base_x+2*(button_width_large+button_x_margin), y=new_y, width=button_width_large, height=button_height)

        return 

    def __onWindowDelete(self):
        if(self.timer != None):
            self.timer.cancel()

        self.stop_button_pressed = 1

        sys.exit()

    def show_kca_connection_ui(self):        
        self.__read_irss_db_configuration_from_ini()
        self.__read_kca_configuration_from_ini()

        self.__make_irss_db_connection_ui()
        self.__make_kca_connection_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.__onWindowDelete)

        self.root.mainloop()  