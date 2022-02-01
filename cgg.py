import passwords
import requests
import json
import utils

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

# Token generation
class OAuth2Client:
    def __init__(self):
        self.username = passwords.alissa.username
        self.password = passwords.alissa.password
        self.client_id = passwords.alissa.username
        self.client_secret = passwords.alissa.password
        self.token_url = passwords.alissa.token_url
        self.session = OAuth2Session(client=LegacyApplicationClient(client_id=self.client_id))

        self._token = None

    def fetch_token(self):

        if self._token:
            return self._token

        response = self.session.fetch_token(token_url=self.token_url,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret)

        if self.session.authorized:
            self._token = response['token_type'] + " " + response['access_token']

        return self._token

    def is_valid_token(self) -> bool:
        return self.session.authorized
    
class cggPatient:
    def __init__(self, token, patient_id, folder_name, accession_number, sex='Unknown'):
    #Should all of these attributes be stored there or can they go somewhere else, e.g. in functions?
        self.token = token
        self.patient_id = patient_id
        self.resource_url = passwords.alissa.bench_url + "/api/2/" + "patients"
        self.folder_name = folder_name
        self.sex = sex
        self.accession_number = accession_number #Perhaps we do not need that one because in our case, the DNAxxx (or the like) names should be used everywhere.

    def exist(self):
        response = requests.get(self.resource_url, params={'accessionNumber': self.patient_id} , headers = {'Authorization' : self.token})
        patient_list = utils.convert_json_to_obj(response.text)
        return patient_list[0] if patient_list is not None and len(patient_list) > 0 else None
#
#    def create(self):
#
#        response = requests.post(self.resource_url, data = json.dumps(patient.__dict__), headers = {'Authorization' : self.create_authorization_header_contents(),'Content-Type': 'application/json'})
#        response.raise_for_status() #If it succeeded, this should be "None".



#
#
# Patient query
#cf api_client.py from row 55, function get_patient_by_name in class PatientPublicApiConrollerClient
#and in bcm.py, from row 85. And then also at the bottom of bcm.py, from row 76 (not sure how that part works).
#
# VCF/file query
#cf bcm.py from row 42 - Check if data file already exists in the system. Function get_data_file_by_Name from api_client.py
#
# Patient post
#cf bcm.py from row 84; functions: get_patient_by_name, create_patient (caution! The create_patient from api_client.py, not from bcm.py) (why are there two functions with the same name? Not practical).
#
# VCF post
#cf bcm.py from row 66 - Upload VCF file. Function add_data_file from api_client.py.
#cf bcm.py from row 109 - Attach VCF file to a patient. Function create_lab_result from api_client.py. 


    
def main():
    oauth2_client = OAuth2Client()
    oauth2_client.fetch_token()
    
    if oauth2_client.is_valid_token():
        newtoken = oauth2_client._token
        print(newtoken)
        patient_id = "test-patient_220105_10" #TODO get this information from SLIMS (most likely: sctx.sample_name)
        folder_name = "Default" #TODO get this information from SLIMS
        patient_sex = "Female" #sctx.slims_info['gender']
        accession_number = "test-patient_220105_1000"
        patient = cggPatient(newtoken, patient_id, folder_name, accession_number, patient_sex)

        patient_by_accession = patient.exist()
        #TODO in the future: depending on whether the patient already exists or not, behavior (e.g. creating a patient) might differ.
        print(patient_by_accession) if patient_by_accession is not None else print("Patient does not exist")

#        #Location and name of VCF: Sctx.snv_cnv_vcf_path

    else:
        print('No token was generated. Investigate!')
   
if __name__ == '__main__':
    main()
