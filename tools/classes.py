import requests
import json
import os

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

class OAuth2Client:
    """Read credentials and return a token."""

    def __init__(self, username, password, token_url):
        # TODO here or in the main() function: enable to choose between the test and production instance. The easiest might be to do something in main().
        # One option is to have all of the arguments below as arguments of __init__ (or at least the ones that do not repeat).
        self.username = username
        self.password = password
        self.client_id = username
        self.client_secret = password
        self.token_url = token_url
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

    def __init__(self, token, bench_url, accession_number,
                 folder_name='Default', sex='UNKNOWN', comments='', family_id=''):
        self.token = token
        self.resource_url = os.path.join(bench_url, 'api/2/patients')
        self.accession_number = accession_number
        self.folder_name = folder_name
        self.sex = sex
        self.comments = comments
        self.family_id = family_id

    def get_existing_patient(self):
        """Return patient entry if it exists."""
        response = requests.get(self.resource_url,
                                params={'accessionNumber': self.accession_number},
                                headers={'Authorization': self.token})
        patient_list = json.loads(response.text)  # List of dict entries FIXME ??
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
                                 data=json.dumps(json_data),
                                 headers={'Authorization': self.token,
                                          'Content-Type': 'application/json'})
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return


class cggVCF:
    """Create an object with information about a VCF.

    Includes functions to check whether a data file exists in Alissa and to upload a data file.
    """

    def __init__(self, token, bench_url, path):
        self.token = token
        self.resource_url_post = os.path.join(bench_url, 'api/2/data_files')
        self.path = path
        self.name = os.path.basename(path)

    def get_data_file_by_name(self):
        """Return a list with information about data file if it already exists in the system."""
        response = requests.get(self.resource_url_post,
                                params={'name': self.name},
                                headers={'Authorization': self.token})
        return json.loads(response.text)

    def post_vcf_to_alissa(self):
        """Create post request for uploading a VCF from local machine to Alissa."""
        fileinfo = (self.name, open(self.path, 'rb'), 'application/octet-stream')
        files_list = [('file', fileinfo)]
        response = requests.post(self.resource_url_post,
                                 params={'type': 'VCF_FILE'},
                                 headers={'Authorization': self.token},
                                 files=files_list)
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return


class cggLabResult:
    """Create an object with information about a lab result in Alissa API.

    The sample identifier is the sample ID in the VCF file header line."""

    def __init__(self, token, bench_url, patient_id, data_file_id, sample_identifier):
        self.token = token
        self.patient_id = patient_id
        self.lab_result_url = os.path.join(bench_url, 'api/2/patients/', str(self.patient_id), 'lab_results')
        self.data_file_id = data_file_id
        self.sample_identifier = sample_identifier

    def get_lab_result(self):
        """Get lab result of a patient using Alissa internal patient ID."""
        response = requests.get(self.lab_result_url,
                                params={'patientId': self.patient_id},
                                headers={'Authorization': self.token})
        return json.loads(response.text)

    def link_vcf_to_patient(self):
        """Create a lab result i.e. link a patient to a VCF file using Alissa's internal identifiers."""
        json_data = {
            'dataFileId': self.data_file_id,
            'sampleIdentifier': self.sample_identifier
        }
        response = requests.post(self.lab_result_url,
                                 data=json.dumps(json_data),
                                 headers={'Authorization': self.token, 'Content-Type': 'application/json'})
        response_body = json.loads(response.text)
        if response_body:
            return response_body['id']
        return
