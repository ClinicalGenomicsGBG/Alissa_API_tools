import requests
import utils
import json

from models import LabResult, Patient,FileInfo
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient


class OAuth2Client:
    def __init__(self):
        self.username = utils.get_config_value('username')
        self.password = utils.get_config_value('password')
        self.client_id = utils.get_config_value('client_id')
        self.client_secret = utils.get_config_value('client_secret')
        self.token_url = utils.get_config_value('auth_token_url') 
        self.session = OAuth2Session(client=LegacyApplicationClient(client_id=self.client_id))

    def fetch_token(self):
        response = self.session.fetch_token(token_url=self.token_url,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret)

        if self.session.authorized:
            return response['token_type'] + " " + response['access_token']
        return None

    def is_valid_token(self) -> bool:
        return self.session.authorized

class BasePublicApiConrollerClient:
    bench_url = utils.get_config_value('bench_url');

    def __init__(self,oauth2_client : OAuth2Client):
        self.oauth2_client = oauth2_client
        self.public_api_url = self.bench_url + "/api/2/" 


    def create_authorization_header_contents(self):
        return self.oauth2_client.fetch_token()

    def is_valid_token(self) ->bool:
        return self.oauth2_client.is_valid_token()
    
class PatientPublicApiConrollerClient(BasePublicApiConrollerClient):
    
    def __init__(self, crypto_service: OAuth2Client):
        super().__init__(crypto_service)
        self.resource_url = self.public_api_url + "patients"
        self.id_parameter_resource_Url = self.resource_url + "{" + "patientId}"


    def get_patient_by_name(self,name):
        response = requests.get(self.resource_url, params={'accessionNumber': name} , headers = {'Authorization' : self.create_authorization_header_contents()})
        response.raise_for_status()
        patient_list = utils.convert_json_to_obj(response.text)
        return patient_list[0] if patient_list is not None and len(patient_list) > 0 else None
    
    def create_patient(self,patient : Patient):
        response = requests.post(self.resource_url, data = json.dumps(patient.__dict__), headers = {'Authorization' : self.create_authorization_header_contents(),'Content-Type': 'application/json'})
        response.raise_for_status()
        response_body = utils.convert_json_to_obj(response.text)
        if response_body is not None:
            return response_body['id']
        return 


class FolderPublicApiConrollerClient(BasePublicApiConrollerClient):
    def __init__(self, crypto_service: OAuth2Client):
        super().__init__(crypto_service)

    

class DataFilePublicApiConrollerClient(BasePublicApiConrollerClient):
    def __init__(self, crypto_service: OAuth2Client):
        super().__init__(crypto_service)
        self.resource_url = self.public_api_url + "data_files"
        self.id_parameter_resource_Url = self.resource_url + "/{" + "dataFileId}"

    def get_data_file_by_Name(self, name) -> list:
        auth = self.create_authorization_header_contents()
        response = requests.get(self.resource_url, params={'name': name} , headers = {'Authorization' : auth})
        response.raise_for_status()
        return utils.convert_json_to_obj(response.text)

    def add_data_file(self, file_info : FileInfo, file_type):
        files_list=[ ('file',(file_info.originalName,open(file_info.originalPath,'rb'),'application/octet-stream'))]
        response = requests.post(self.resource_url, params={'type': file_type} , headers = {'Authorization' : self.create_authorization_header_contents()},files=files_list)
        response.raise_for_status()
        response_body = utils.convert_json_to_obj(response.text)
        if response_body is not None:
            return response_body['id']
        return;


class LabResultPublicApiConrollerClient(BasePublicApiConrollerClient):
    def __init__(self, crypto_service: OAuth2Client):
        super().__init__(crypto_service)
        self.id_parameter_resource_Url = self.public_api_url + "lab_results/" + "{" + "labResultId}/"
        self.patient_lab_result_url = self.public_api_url + "patients/{" + "patientId}/" + "lab_results"
    
    def get_lab_result_by_Id(self, id):
        response = requests.get(self.id_parameter_resource_Url.format(labResultId=str(id)), headers = {'Authorization' : self.create_authorization_header_contents()})
        response.raise_for_status()
        return response.text
    
    def create_lab_result(self,patient_id,lab_result: LabResult):
        response = requests.post(self.patient_lab_result_url.format(patientId=str(patient_id)), data = json.dumps(lab_result.__dict__), headers = {'Authorization' : self.create_authorization_header_contents(),'Content-Type': 'application/json'})
        response.raise_for_status()
        response_body = utils.convert_json_to_obj(response.text)
        if response_body is not None:
            return response_body['id']
        return