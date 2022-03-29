#This script contains functions and classes enabling the essential steps of the interaction with the Alissa API: obtaining an authentification token; creating a patient; loading a VCF file; and linking a patient and a VCF (creating a "lab result").
# The main() function will retrieve a token; check whether a patient exists (in Alissa) and if not, create it; check whether a data file exists (in Alissa) and if not, create it; and link patient and VCF.
# Usage (to print the help message): module load anaconda2/4.1.0; source activate wopr_alissa; python cgg.python --help
# To use the production instance, replace passwords_test_instance by passwords 

#TODO add an exception if token is not generated by function .fetch_token(); remove the exception from the main() function.

import passwords_test_instance as passwords
import requests
import json
import os
import chunk_vcf
import click

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

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

    In WOPR, the comments and family_id fields are not used. folder_name is usually Klinisk Genetik (KG) or Klinisk Kemi (KK).
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

    Includes functions to check whether a data file exists in Alissa and to upload a data file.
    """
    def __init__(self, token, path): 
        self.token = token
        self.path = path
        self.resource_url_post = os.path.join(passwords.alissa.bench_url, 'api/2/data_files') 
        self.name = os.path.basename(path)

    def get_data_file_by_name(self):
        """Return a list with information about data file if it already exists in the system."""
        response = requests.get(self.resource_url_post,
                                params = {'name': self.name},
                                headers = {'Authorization': self.token})
        return json.loads(response.text)  

    def post_vcf_to_alissa(self):
        """Create post request for uploading a VCF from local machine to Alissa."""
        fileinfo = (self.name, open(self.path,'rb'), 'application/octet-stream')
        files_list=[ ('file', fileinfo) ]
        response = requests.post(self.resource_url_post,
                             params = {'type': 'VCF_FILE'},
                             headers = {'Authorization': self.token},
                             files = files_list)
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return

class cggLabResult:
    """Create an object with information about a lab result in Alissa API.

    The sample identifier is the sample ID in the VCF file header line."""
    def __init__(self, token, patient_id, data_file_id, sample_identifier):
         self.token = token
         self.patient_id = patient_id
         self.data_file_id = data_file_id
         self.sample_identifier = sample_identifier
         self.lab_result_url = os.path.join(passwords.alissa.bench_url, 'api/2/patients/', str(self.patient_id), 'lab_results')

    def get_lab_result(self):
        """Get lab result of a patient using Alissa internal patient ID."""
        response = requests.get(self.lab_result_url,
                                params = {'patientId': self.patient_id},
                                headers = {'Authorization': self.token})
        return json.loads(response.text) 

    def link_vcf_to_patient(self):
        """Create a lab result i.e. link a patient to a VCF file using Alissa's internal identifiers."""
        json_data = {
            'dataFileId': self.data_file_id,
            'sampleIdentifier': self.sample_identifier
        }
        response = requests.post(self.lab_result_url,
                            data = json.dumps(json_data),
                            headers = {'Authorization': self.token, 'Content-Type': 'application/json'})
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return

def create_patient(token, accession, sex, alissa_folder):
    """Create a patient in Alissa (unless the patient already exists, in which case a message is returned). Return the internal patient id."""
    patient = cggPatient(token, accession, alissa_folder, sex)
    if not patient.exists():
        patient_id = patient.create()
    else:
        print('Patient exists.')
        existing_patient = patient.get_existing_patient()
        patient_id = existing_patient['id']
    print(f'The patient ID is: {patient_id}.')
    return(patient_id)

def create_datafile(token, path):
    """Create a datafile in Alissa (unless the data file already exists). Return the internal datafile id."""
    vcf = cggVCF(token, path)
    data_file = vcf.get_data_file_by_name()
    if len(data_file) == 0:
        data_file_id = vcf.post_vcf_to_alissa()
    else: 
        print('A VCF file with the same name already exists. Not attempting to upload it again.')
        data_file_id = data_file[0]['id']
    print(f'The data file ID is: {data_file_id}.')
    return(data_file_id)

def create_lab_result(token, patient_id, datafile_id, name_in_vcf):
    """Create a lab result in Alissa (unless the lab result already exists)."""
    labresult = cggLabResult(token, patient_id, datafile_id, name_in_vcf)
    prior_labresult = labresult.get_lab_result()
    if len(prior_labresult) > 0:
        exist_labresult = []
        exist_datafile = []
        for result in prior_labresult:
            exist_labresult.append(result['id'])
            exist_datafile.append(result['dataFileId'])
        if datafile_id in exist_datafile:
            i = exist_datafile.index(datafile_id)
            labresult_id = exist_labresult[i]
            print(f'The lab result for patient {patient_id} and data file {datafile_id} already exists: {labresult_id}. Skipping creating a new one.')
        else:
            labresult_id = labresult.link_vcf_to_patient()
            print(f'The lab result ID for patient {patient_id} and data file {datafile_id} is: {labresult_id}.')
    else:
        labresult_id = labresult.link_vcf_to_patient()
        print(f'The lab result ID for patient {patient_id} and data file {datafile_id} is: {labresult_id}.')
    return labresult_id

@click.command()
@click.option('-a', '--accession', required=True,
             help='Patient accession number')
@click.option('-s', '--sex', default='UNKNOWN', type=click.Choice(['FEMALE', 'MALE', 'UNKNOWN']),
             help='Sex of the sample')
@click.option('-f', '--alissa_folder', default='Default',
             type=click.Choice(['BCF demo', 'CRC pipeline validation', 'CRE2 Reference set files', 'Default', 'ExomeValidation', 'Klinisk Genetik', 'Klinisk Genetik - Forskning', 'Klinisk kemi', 'Validation WGS']),
             help='Patient folder in Alissa, for example "Klinisk kemi" or "Klinisk Genetik"')
@click.option('-v', '--vcf_path', required=True, type=click.Path(exists=True),
              help='Path to input VCF file')
@click.option('-o', '--output_folder', default='/tmp',
              help='Path to a folder where the VCF will be written if the input VCF is larger than the size argument. In that case, files will be loaded to Alissa from that folder')
@click.option('-s', '--size', required=True, type=int,
              help='Size in bp. If the VCF exceed this size, it will be split into 2, 3 or 4 VCFs')
@click.option('-n', '--name_in_vcf', required=True,
             help='Sample ID in the VCF header row')
def main(accession, sex, alissa_folder, vcf_path, output_folder, size, name_in_vcf):
    oauth2_client = OAuth2Client()
    token = oauth2_client.fetch_token()

    if token:
        patient_id = create_patient(token, accession, sex, alissa_folder)
        vcfs = chunk_vcf.prepare_and_split_vcf(vcf_path, output_folder, size)
        for path in vcfs:
            datafile_id = create_datafile(token, path)
            create_lab_result(token, patient_id, datafile_id, name_in_vcf)
	
    else:
        # TODO Add a raise for custom Exception or built-in
        raise Exception('No token was generated. Investigate!')
   
if __name__ == '__main__':
    main()
