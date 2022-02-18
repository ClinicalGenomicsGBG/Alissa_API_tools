#TODO add an exception if token is not generated by function .fetch_token(); remove the exception from the main() function.

import passwords
import requests
import json

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
#from chunk_vcf import FileInfo #TODO decide whether to define the class within cgg.py or keep it in chunk_vcf.py; package more of the chunk_vcf.py code into classes/functions. If I want to import only the class FileInfo from chunk_vcf.py, I need to package the rest of the logic in functions/main()/etc.

class FileInfo:
    """Create object with basic information to be used in VCF upload to Alissa via the API."""
    def __init__(self,originalPath,originalName):
        self.originalPath = originalPath
        self.originalName = originalName


# Token generation
class OAuth2Client:
    """Read credentials and return a token."""
    def __init__(self):
        self.username = passwords.alissa.username
        self.password = passwords.alissa.password
        self.client_id = passwords.alissa.username
        self.client_secret = passwords.alissa.password
        self.token_url = passwords.alissa.token_url
        self.session = OAuth2Session(client=LegacyApplicationClient(client_id=self.client_id))

        # TODO Add token timer
        self._token = None

    def fetch_token(self):
        """Fetch a token that is used for commands to Alissa such as creating a patient."""
        # TODO Add check for time since token made
        if self._token:
            return self._token

        response = self.session.fetch_token(token_url=self.token_url,
                                            username=self.username,
                                            password=self.password,
                                            client_id=self.client_id,
                                            client_secret=self.client_secret)
        # FIXME This could be done better
        if self.session.authorized:
            self._token = response['token_type'] + " " + response['access_token']

        return self._token

class cggPatient:
    """Create an object with information about a patient.

    In WOPR, the accession_number and the patient_id are the same; the comments and family_id fields are not used. folder_name is usually KG, KK or PAT.
    """
    def __init__(self, token, patient_id, accession_number,
                 folder_name='Default', sex='UNKNOWN', comments='', family_id=''):
        self.token = token
        self.patient_id = patient_id
        self.accession_number = accession_number

        self.folder_name = folder_name
        self.sex = sex
        self.comments = comments
        self.family_id = family_id

        self.resource_url = passwords.alissa.bench_url + "/api/2/" + "patients"

    def get_existing_patient(self):
        """Return patient entry if it exists."""
        response = requests.get(self.resource_url,
                                params={'accessionNumber': self.patient_id},
                                headers = {'Authorization' : self.token})
        return json.loads(response.text) # List of dict entries FIXME ??

    def exists(self):
        """Return patient entry exists."""
        return bool(self.get_existing_patient())

    def create(self):
        """Create the patient."""
        json_data = {
            'accessionNumber': self.accession_number,
            'folderName': self.folder_name,
            'gender': self.sex,
            'comments': self.comments,
            'familyIdentifier': self.family_id
        }
        response = requests.post(self.resource_url,
                                 data = json.dumps(json_data),
                                 headers = {'Authorization' : self.token,
                                            'Content-Type': 'application/json'})
        response.raise_for_status() #TODO is that needed?
        return response

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

#TODO add a function (or a step in post_vcf_to_alissa) to check whether a file with the same name already exists. Otherwise it will be replaced.
def post_vcf_to_alissa(file_info : FileInfo, token):
    """Create post request for uploading a VCF from local machine to Alissa."""
    files_list=[ ('file',(file_info.originalName,open(file_info.originalPath,'rb'),'application/octet-stream'))]
    resource_url_postvcf = passwords.alissa.bench_url + "/api/2/" + "data_files"
    response = requests.post(resource_url_postvcf,
                             params={'type': 'VCF_FILE'},
                             headers = {'Authorization' : token},
                             files=files_list)
    response_body = json.loads(response.text)
    if response_body is not None:
        return response_body['id']
    return
    
def main():
    oauth2_client = OAuth2Client()
    token = oauth2_client.fetch_token()

    if token:
        ##Test: create patient, check whether it exists.
        #patient_id = "test-patient_220214_2" #TODO get this information from SLIMS (most likely: sctx.sample_name)
        #folder_name = "Default" #TODO get this information from SLIMS
        #patient_sex = "FEMALE" #sctx.slims_info['gender']
        #accession_number = "test-patient_220214_2"
        #patient = cggPatient(token, patient_id, accession_number, folder_name, patient_sex)
        #
        #if patient.exists():
        #    print('Patient exists.')
        #    return True # TODO what to return?
        #else:
        #    response = patient.create()
        
        #Test: post a VCF file
        path = '/home/xbregw/Alissa_upload/VCFs/chunks/NA24143_191108_AHVWHGDSXX_SNV_CNV_germline_chr1-8.vcf.gz' #Location and name of VCF in slims: Sctx.snv_cnv_vcf_path
        name = 'NA24143_191108_AHVWHGDSXX_SNV_CNV_germline_chr1-8.vcf.gz'
        vcf_file_info = FileInfo(path,name) #Or how should the values be filled in?
        data_file_id = post_vcf_to_alissa(vcf_file_info, token)
        print(data_file_id)

    else:
        # TODO Add a raise for custom Exception or built-in
        raise Exception('No token was generated. Investigate!')
   
if __name__ == '__main__':

    main()
