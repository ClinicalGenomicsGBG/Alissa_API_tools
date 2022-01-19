import passwords
import requests

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
    def __init__(self, token, patient_id):
        self.token = token
        self.patient_id = patient_id #Can these be defined as arguments of cggPatien?
        self.resource_url = passwords.alissa.bench_url + "/api/2/" + "patients"

#Does the function below have to be repeated? Can it be defined in the main function instead? Or is it possible to save a token instead? Perhaps it is better to ask for a new token at every action, in case that the token expires...        
#    def create_authorization_header_contents(self):
#        return self.oauth2_client.fetch_token()        

    def exist(self):
        #Where does "name" come from? I am trying to replace it by patient_id.
        response = requests.get(self.resource_url, params={'accessionNumber': self.patient_id} , headers = {'Authorization' : self.token})
        return response.status_code == 200

#    def create(self, folder_name, gender='Unknown'):
#
#        response = requests.post(self.resource_url, data = json.dumps(patient.__dict__), headers = {'Authorization' : self.create_authorization_header_contents(),'Content-Type': 'application/json'})
#        response.raise_for_status()
    
def main():
    oauth2_client = OAuth2Client()
    oauth2_client.fetch_token()
    
    if oauth2_client.is_valid_token():
        newtoken = oauth2_client._token
        print(newtoken)
        patient_id = "test-patient-20220119_1" #TODO get this information from SLIMS (most likely: sctx.sample_name)
        patient = cggPatient(newtoken,patient_id)
        patient.exist()

    else:
        print('No token was generated. Investigate!')
   
if __name__ == '__main__':
    main()
