#This script contains functions and classes enabling the essential steps of the interaction with the Alissa API: obtaining an authentification token; creating a patient; loading a VCF file; and linking a patient and a VCF (creating a "lab result").
# The main() function will retrieve a token; check whether a patient exists (in Alissa) and if not, create it; check whether a data file exists (in Alissa) and if not, create it; and link patient and VCF.
# At the moment the parameters should be modified directly in the main() function. The parameters to modify are: accession_number, path, and name_in_vcf.
# "path" is the path to a VCF file. If it's larger than 240M, the file will be splitted into two and both are uploaded and linked to patient in Alissa.
# Usage: module load anaconda2/4.1.0; source activate wopr_alissa; python cgg.python
# To use the production instance, replace passwords_test_instance by passwords 

#TODO add an exception if token is not generated by function .fetch_token(); remove the exception from the main() function.

import passwords_test_instance as passwords
import requests
import json
import os
import chunk_vcf

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

class FileInfo:
    """Create object with basic information to be used in VCF upload to Alissa via the API."""
    def __init__(self, originalPath, originalName):
        self.originalPath = originalPath
        self.originalName = originalName

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

    In WOPR, the comments and family_id fields are not used. folder_name is usually Klinisk Genetik (KG) or Klinisk kemi (KK).
    """
    def __init__(self, token, accession_number,
                 folder_name='Default', sex='UNKNOWN', comments='', family_id=''):
        self.token = token
        self.accession_number = accession_number
        self.folder_name = folder_name
        self.sex = sex
        self.comments = comments
        self.family_id = family_id
        self.resource_url = os.path.join(passwords.alissa.bench_url, 'api/2/patients')

    def get_existing_patient(self):
        """Return patient entry if it exists."""
        response = requests.get(self.resource_url,
                                params = {'accessionNumber' : self.accession_number},
                                headers = {'Authorization' : self.token})
        patient_list = json.loads(response.text) # List of dict entries FIXME ??
        if patient_list:
            return patient_list[0]
        return None
        
    def exists(self):
        """Return patient entry exists."""
        return bool(self.get_existing_patient())

    def create(self):
        """Create the patient. Return the internal Alissa ID for the patient."""
        json_data = {
            'accessionNumber': self.accession_number,
            'folderName': self.folder_name,
            'gender': self.sex,
            'comments': self.comments,
            'familyIdentifier': self.family_id
        }
        response = requests.post(self.resource_url,
                                 data = json.dumps(json_data),
                                 headers = {'Authorization': self.token,
                                            'Content-Type': 'application/json'})
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return        

class cggVCF:
    """Create an object with information about a VCF.

    Includes functions to check wehther a data file exists in Alissa, and to upload a data file.
    """
    def __init__(self, token, vcf, resource_url_post): #I might need to pass a FileInfo object here. 
        self.token = token
        self.vcf = vcf
        self.resource_url_post = os.path.join(passwords.alissa.bench_url, 'api/2/data_files') 

    def get_data_file_by_name(self):
        """Return a list with information about data file if it already exists in the system."""
        response = requests.get(self.resource_url_postvcf,
                                params = {'name': self.vcf},
                                headers = {'Authorization': self.token})
        return json.loads(response.text)  

    def post_vcf_to_alissa(file_info: FileInfo, token): #TODO Here I need to feed in the information in a different way. Can FileInfo be part of self?
        """Create post request for uploading a VCF from local machine to Alissa."""
        fileinfo = (file_info.originalName, open(file_info.originalPath,'rb'), 'application/octet-stream')
        files_list=[ ('file', fileinfo) ]
        response = requests.post(resource_url_post,
                             params = {'type': 'VCF_FILE'},
                             headers = {'Authorization': token},
                             files = files_list)
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return

#TODO should this function be included in the class cggVCF and if yes, how do I deal with the arguments?
def link_vcf_to_patient(patient_id, data_file_id, sample_identifier, token):
    """Create a lab result i.e. link a patient to a VCF file, using Alissa's internal identifiers.

    The sample identifier is the sample ID in the VCF file header line.
    """
    lab_result_url = os.path.join(passwords.alissa.bench_url, 'api/2/patients/', str(patient_id), 'lab_results')
    json_data = {
        'dataFileId': data_file_id,
        'sampleIdentifier': sample_identifier
    }
    response = requests.post(lab_result_url,
                            data = json.dumps(json_data),
                            headers = {'Authorization': token, 'Content-Type': 'application/json'})
    response_body = json.loads(response.text)
    if response_body:
        return response_body['id']
    return

 
def main():
    oauth2_client = OAuth2Client()
    token = oauth2_client.fetch_token()

    if token:
	
	#Parameters required for 1-creating patient, 2-uploading VCF file and 3-linking patient and VCF file.
        accession_number = "test-patient_220309_1" #SLIMS: Sctx.sample_name
        folder_name = "Default" #SLIMS: department_translate[Sctx.slims_info['department']], default: "Default"
        patient_sex = "MALE" #SLIMS: Sctx.slims_info['gender'], default: "UNKNOWN"
        path = '/home/xbregw/Alissa_upload/VCFs/known_variants_20220309.vcf.gz' #SLIMS: Sctx.snv_cnv_vcf_path
        name_in_vcf = "NA12878" #That is the sample ID in the VCF header row. In WOPR, it should be the same as Sctx.sample_name

        #Check whether a patient exists, if not: create it. In both cases: return internal patient id.
        patient = cggPatient(token, accession_number, folder_name, patient_sex)
        if patient.exists():     #An alternative to this function is to check whether the response of get_existing_patient is "None" (cf Agilent bcm.py row 88).
            print('Patient exists.')
            existing_patient = patient.get_existing_patient()
            patient_id = existing_patient['id']
        else:
            patient_id = patient.create()
        print(patient_id)

        #Check size of VCF file. If larger than a given size (240 MiB for Alissa): split it. Return the paths to the chunks (or to the VCF of choice).
        vcfs = chunk_vcf.prepare_and_split_vcf(path, '/home/xbregw/Alissa_upload/VCFs/chunks', 240_000_000)
        
        #Loop over the items in vcfs.
        for path in vcfs:
            #Check whether a data file exists, if not: upload it. In both cases: return internal data file id.
            name = os.path.basename(path)
            data_file = get_data_file_by_name(name, token)
            if len(data_file) > 0:
                print('A VCF file with the same name already exists. Not attempting to upload it again.')
                data_file_id = data_file[0]['id']
            else: 
                vcf_file_info = FileInfo(path,name)
                data_file_id = post_vcf_to_alissa(vcf_file_info, token)
            print(data_file_id)

            #Link data file to patient (i.e. create a lab result). If the lab result already exists: this will result in an error.
            labresult = link_vcf_to_patient(patient_id, data_file_id, name_in_vcf, token)
            print(labresult)

    else:
        # TODO Add a raise for custom Exception or built-in
        raise Exception('No token was generated. Investigate!')
   
if __name__ == '__main__':
    main()
