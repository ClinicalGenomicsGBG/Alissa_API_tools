from configparser import Error
import json
from typing import Text
from api_clients import PatientPublicApiConrollerClient,DataFilePublicApiConrollerClient,LabResultPublicApiConrollerClient,OAuth2Client
from models import FileInfo, LabResult, OrderRequest, Patient,Response
import utils
import os
import requests
import sys
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError,CustomOAuth2Error

genders = {'MALE', 'FEMALE', 'UNKNOWN'}
oauth2_client = OAuth2Client()
patient_rest_client = PatientPublicApiConrollerClient(oauth2_client)
data_file_rest_client = DataFilePublicApiConrollerClient(oauth2_client)
lab_result_rest_client = LabResultPublicApiConrollerClient(oauth2_client)

def create_patient(request : OrderRequest) -> Response:
    resp_str = utils.validate_all_config()
    user_name = utils.get_config_value('username')
    if resp_str is not None :
        return Response(user_name,500,resp_str)
    file_name = request.alissa_file_name
    patient_request = request.patient

    response = validate_request(user_name,request)
    if response is not None:
        return response
    
    
    # Check for VCF file authenticity
    vcf_file_info = None
    try:
        vcf_file_info = download(request.file_path,file_name)
    except :
        return Response(user_name,500,"Invalid VCF file path")  

    if vcf_file_info.currentSize == 0:
        return Response(user_name,500,"Invalid VCF file")

    
    # Check if data file already exists in the system.
    try:
        data_file = data_file_rest_client.get_data_file_by_Name(file_name)
        if len(data_file) > 0:
            return Response(user_name,500,"VCF file already exists in the system")
    except InvalidGrantError as err:
        return Response(user_name,500,"Invalid username or password")
    except CustomOAuth2Error as err:
        return Response(user_name,500,"Invalid client id or client secret")
    except requests.exceptions.HTTPError as error:
        code = error.response.status_code
        if code == 401:
            status_message = "User not found" if data_file_rest_client.is_valid_token()  else "Unable to fetch valid authentiaction token"
            return Response(user_name,500,status_message)
        elif code == 403:
            return Response(user_name,500,"User doesn\'t have permission on folder")
        return Response(user_name,500,str(error))
    except requests.exceptions.ConnectionError as errc:
        return Response(user_name,500,"Error Connecting: " + str(errc))
    except requests.exceptions.RequestException as err:
        return Response(user_name,500,str(err))
    except requests.exceptions.Timeout as errt:
        return Response(user_name,500,"Timeout Error:" + str(errt))
    
    #Upload VCF File.
    data_file_id = None
    try:
        data_file_id = data_file_rest_client.add_data_file(vcf_file_info,request.file_type)
    except requests.exceptions.ConnectionError as errc:
        return Response(user_name,500,"Error Connecting: " + str(errc))
    except requests.exceptions.HTTPError as error:
        response_text =   error.response.text if error.response.text is not None else ""
        if  response_text.__contains__("fileType"):
            return Response(user_name,500,"VCF file parser not found")
        elif response_text.__contains__("ERROR_PARSING_DATAFILE"):
            return Response(user_name,500,"Error parsing VCF file")
        return Response(user_name,500,str(error))
    except requests.exceptions.RequestException as err:
        return Response(user_name,500,str(err))
    except requests.exceptions.Timeout as errt:
        return Response(user_name,500,"Timeout Error:" + str(errt))
    
    # Create patient/Update patient.
    patient_id=None
    try:
        patient_by_accession = patient_rest_client.get_patient_by_name(patient_request.accession)
        if patient_by_accession is not None:
           #fetch id from existing patient
           patient_id = patient_by_accession['id']
        else:   
            patient = Patient(patient_request.accession,patient_request.comments,patient_request.family_id,request.patient_folder,patient_request.sex)
            patient_id = patient_rest_client.create_patient(patient)
    except requests.exceptions.ConnectionError as errc:
        return Response(user_name,500,"Error Connecting: " + str(errc))
    except requests.exceptions.HTTPError as error:
        code = error.response.status_code
        response_text =   error.response.text if error.response.text is not None else ""
        if code == 403 or (response_text.__contains__("ERROR_FOLDER_WITH_NAME_NOT_ACCESSIBLE")):
            return Response(user_name,500,"User doesn\'t have permission on folder")
        elif response_text.__contains__("ERROR_PATIENT_FOLDER_EMPTY"):
            return Response(user_name,500,"Invalid folder name")
        return Response(user_name,500,str(error))
    except requests.exceptions.RequestException as err:
        return Response(user_name,500,str(err))
    except requests.exceptions.Timeout as errt:
        return Response(user_name,500,"Timeout Error:" + str(errt))

    # Attach VCF file to a patient
    lab_result_id = None
    try:
        lab_result = LabResult(data_file_id,request.patient.sample)
        lab_result_id = lab_result_rest_client.create_lab_result(patient_id,lab_result)
    except requests.exceptions.ConnectionError as errc:
        return Response(user_name,500,"Error Connecting: " + str(errc))
    except requests.exceptions.HTTPError as error:
        response_text =   error.response.text if error.response.text is not None else ""
        if response_text.__contains__("ERROR_SAMPLE_ID_NOT_FOUND"):
            return Response(user_name,500,"Sample name mismatched")
        elif response_text.__contains__("ERROR_UNEXPECTED_LABRESULT_CREATE"):    
            return Response(user_name,500,"Unexpected error occured during lab result creation.\n"+str(error))
        return Response(user_name,500,"Unable to create lab result.\n"+str(error))    
    except requests.exceptions.RequestException as err:
        return Response(user_name,500,str(err))
    except requests.exceptions.Timeout as errt:
        return Response(user_name,500,"Timeout Error:" + str(errt))

    return Response(user_name,200,"Submission Ok",patient_request.accession,lab_result_id)


#download vcf file from local machine
def download(path,file_name):
    if os.path.isfile(path):
        name = os.path.basename(path)
        size = os.path.getsize(path)
        return FileInfo(path,file_name,size,path,name,size)
    else:
        raise Exception("File Not Found [%s]" , path)


# Validate input requests.
def validate_request(user_name, request: OrderRequest) -> Response:
    if utils.isBlankStr(request.alissa_file_name):
        return Response(user_name,500,"'alissa_file_name' parameter is empty")
    elif utils.isBlankStr(request.file_path):
        return Response(user_name,500,"'file_path' parameter is empty")
    elif utils.isBlankStr(request.file_type):
        return Response(user_name,500,"'file_type' parameter is empty")
    elif utils.isBlankStr(request.patient_folder):
        return Response(user_name,500,"'patient_folder' parameter is empty")
    elif request.patient is None:
        return Response(user_name,500,"'patient' parameter is empty")
    else:
        patient_request = request.patient
        if utils.isBlankStr(patient_request.accession):
            return Response(user_name,500,"'accession' parameter is empty")
        elif utils.isBlankStr(patient_request.family_id):
            return Response(user_name,500,"'family_id' parameter is empty")
        elif utils.isBlankStr(patient_request.comments):
            return Response(user_name,500,"'comments' parameter is empty")
        elif utils.isBlankStr(patient_request.sample):
            return Response(user_name,500,"'sample' parameter is empty")
        elif utils.isBlankStr(patient_request.sex):
            return Response(user_name,500,"'sex' parameter is empty")
        else:
            if patient_request.sex not in genders:
                return Response(user_name,500,"Invalid value for 'sex' parameter")
    return None


if __name__  == '__main__':
    
    try:
        args = sys.argv
        args_len = len (args)
        request = None

        if args_len is 2:
            input_json_text = str(args[1]).strip()
            request =  OrderRequest(**utils.convert_json_to_obj(input_json_text))
        else : 
            print("Script can only accept 2 arguments")
            sys.exit()

        response = create_patient(request)
        response_dict= response.__dict__
        if response.accession is  None:
            response_dict.pop("accession")
        if response.lab_result_id is  None:
            response_dict.pop("lab_result_id")
        
        print()
        print(utils.dumps(response_dict))       
    
    except Exception as e: 
        print(e.args)
