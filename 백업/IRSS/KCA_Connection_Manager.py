import requests
import json

class KCA_Connection_Manager(object):
    def __init__(self):
        self.service_provider_list = ['SK','KT','LG']
        self.service_type_list = ['2G','3G','4G','5G', 'Other']

        self.target_area_name_list = []

        self.url = "https://spectrummap.kr/openapiNew.do"
        self.access_token_string = ""
        self.headers = {
            'Cookie': ''
        }

    def set_service_provider_list(self, service_provider_list):
        self.service_provider_list = service_provider_list

    def set_service_type_list(self, service_type_list):
        self.service_type_list = service_type_list    

    def set_spectrummap_site_url(self, url_string):        
        self.url = "https://spectrummap.kr/openapiNew.do"

    def set_target_area_name_list(self, target_area_name_list):
        self.target_area_name_list = target_area_name_list

    def set_access_token(self, access_token_string):
        self.access_token_string = access_token_string

    def set_header_cookie(self, cookie_string):
        self.header_cookie_string = cookie_string
        self.headers = {
            'Cookie': cookie_string
        }

    def get_jsontext_for_area_from_web(self, rds_sta_cd:str, bs_type:int, service_type:str, service_provider_name:str, \
                                                area_name:str, year:int, index:int, timeout_sec:int, num_retry:int):
        year_last_two_digit_ten = int(year / 10) % 10
        year_last_two_digit_one = (year % 10)        

        url_to_access = self.url + "?key=" + self.access_token_string + "&searchId=10" \
            + ("&RDS_STA_CD=%s" % (rds_sta_cd))\
            + ("&RDS_PMS_NO=%d" % (bs_type)) \
            + str(year) \
            + "&SERVICE_CD=" + service_type \
            + "&CUS_CD=" + service_provider_name \
            + "&RDS_TRS_ADR=" + area_name \
            + ("&SYS_CHG_DTM_ST=%d%d/01/01" % (year_last_two_digit_ten, year_last_two_digit_one) ) \
            + ("&SYS_CHG_DTM_ED=%d%d/12/31" % (year_last_two_digit_ten, year_last_two_digit_one) ) \
            + "&pSize=500&pIndex=" + str(index)
        payload = {} 

        for idx in range(0, num_retry):
            print("요청주소(접속시도 %d/%d) : " % (idx+1, num_retry), url_to_access)
            try:            
                response = requests.request("GET", url_to_access, headers=self.headers, data=payload, timeout=timeout_sec)
                js3 = response.text
                return js3
            except:
                print("Timeout : %d/%d" % (idx+1, num_retry))
                continue

        return None

    def get_result_code_from_kca_json_object(self, kca_json_object):
        result_code = kca_json_object.get("RESULT_CODE")
        return result_code

    def analysis_result_code(self, result_code:str or None) -> tuple[bool, bool, str]:        
        is_error = False
        is_next_iteration = False    
        message_str = ""    
        if(result_code == None):
            is_error = False
            is_next_iteration = True
            message_str = "데이터 오류 (json 객체 구성/분석에 실패하였습니다.)"            
        elif(result_code == "INFO-200"):
            is_error = False
            is_next_iteration = True
            message_str = "해당 데이터가 없습니다."
        elif(result_code == "INFO-300"):
            is_error = True
            message_str = "관리자에 의해 인증키 사용이 제한되었습니다."

        test_val = "ERROR" in result_code
        if(test_val):
            is_error = True
            message_str = "KCA 연결 오류 발생"
        else:
            message_str = "정상"

        return is_error, is_next_iteration, message_str


        


        

