import json
import time
import configparser
from models import OrderRequest

config = configparser.ConfigParser()
config.read('communication.ini')
section = 'bcm'

def convert_json_to_obj(input_json_text):
    input_json = json.loads(input_json_text)
    return input_json

def dumps(obj):
    return json.dumps(obj)

def generate_timestamp():
    return str(round(time.time() * 1000))

def get_config_value(key):
    return config[section][key]

# check if string is empty or not
def isBlankStr(myString):
    return not(myString and myString.strip())

def validate_all_config():
    if isBlankStr(get_config_value("base_url")):
        return "'base_url' parameter is empty"
    elif isBlankStr(get_config_value("username")):
        return "'username' parameter is empty"
    elif isBlankStr(get_config_value("password")):
        return "'password' parameter is empty"
    elif isBlankStr(get_config_value("client_id")):
        return "'client_id' parameter is empty"
    elif isBlankStr(get_config_value("client_secret")):
        return "'client_secret' parameter is empty"
    elif isBlankStr(get_config_value("bench_url")):
        return "'bench_url' parameter is empty"
    elif isBlankStr(get_config_value("auth_token_url")):
        return "'auth_token_url' parameter is empty"
    return None



# temporory method - We are not aware of input 
def load_request_data():
    input_json_text= '''{
                "file_path": "D:/Agilent/VCF Files/VCF_Files/input_hg38.vcf",
                "alissa_file_name": "order_alissa_filename",
                "file_type": "VCF_FILE",
                "patient_folder": "Default",
                "patient": {
                    "accession": "patient_",
                    "sex": "UNKNOWN",
                    "family_id": "test family id",
                    "comments": "Verify Patient creation",
                    "sample": "Trio"
                    }
                }'''

    time_stamp = generate_timestamp()
    request =  OrderRequest(**convert_json_to_obj(input_json_text))
    request.patient.accession += time_stamp
    request.alissa_file_name += time_stamp
    return request