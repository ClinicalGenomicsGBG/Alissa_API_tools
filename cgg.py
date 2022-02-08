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

        # TODO Add token timer
        self._token = None

    def fetch_token(self):
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
    def __init__(self, token, patient_id, accession_number,
                 folder_name='Default', sex='UNKNOWN', comments='', family_id=''):
        self.token = token
        self.patient_id = patient_id
        self.accession_number = accession_number #Perhaps we do not need that one because in our case, the DNAxxx (or the like) names should be used everywhere.

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
        return utils.convert_json_to_obj(response.text) # List of dict entries FIXME ??

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
        response.raise_for_status()  #NOTE: If it succeeds, this should return "None".
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


    
def main():
    oauth2_client = OAuth2Client()
    token = oauth2_client.fetch_token()

    if token:
        patient_id = "test-patient_220203" #TODO get this information from SLIMS (most likely: sctx.sample_name)
        folder_name = "Default" #TODO get this information from SLIMS
        patient_sex = "FEMALE" #sctx.slims_info['gender']
        accession_number = "test-patient_220203"
        patient = cggPatient(token, patient_id, accession_number, folder_name, patient_sex)

        if patient.exists():
            print('Patient exists.')
            return True  # TODO What to return?

        #TODO in the future: depending on whether the patient already exists or not, behavior (e.g. creating a patient) might differ.
        response = patient.create()

#        #Location and name of VCF: Sctx.snv_cnv_vcf_path
    else:
        # TODO Add a raise for custom Exception or built-in
        print('No token was generated. Investigate!')
   
if __name__ == '__main__':
    main()
