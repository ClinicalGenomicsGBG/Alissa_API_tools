

# Token generation
from requests_oauthlib import OAuth2Session
# TODO Switch from get_config (config.ini)
class OAuth2Client:
    def __init__(self):
        self.username = utils.get_config_value('username')
        self.password = utils.get_config_value('password')
        self.client_id = utils.get_config_value('client_id')
        self.client_secret = utils.get_config_value('client_secret')
        self.token_url = utils.get_config_value('auth_token_url')
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

        self.is_valid_toke(self._token)
        return self._token

    def is_valid_token(self) -> bool:
        return self.session.authorized


class cggPatient:
    def __init__(self, token, patient_id):
        self.token = token
        self.patient_id = patient_id

    def exist(self):
        response = requests.get(self.resource_url, params={'accessionNumber': name} , headers = {'Authorization' : self.create_authorization_header_contents()})
        return response.returncode == 200

        # list_of_patient = request.post()
        # return self.patient_id in list_of_patients
        #
    def create(self, folder_name, gender='Unknown'):

        response = requests.post(self.resource_url, data = json.dumps(patient.__dict__), headers = {'Authorization' : self.create_authorization_header_contents(),'Content-Type': 'application/json'})
        response.raise_for_status()


class ccgFilePreChunk:
    def __init__(self, file_path):
        self.file_path = file_path


    def get_size(self):
        return os.stat.size(self.file_path)

    def chunk(self, path):
        chunk_paths = []
        # logic
        #
        return chunk_paths

# Logic of splitting

class cggFile:
    def __init__(self, token, file_path):
        self.token = token
        self.file_path = file_path

    def exist(self):
        response = requests.post()
        return response

    def upload(self, path, file_type='VCF_FILE'):
        return response

#
#
# Patient query
#
#
# VCF/file query
#
#
#
# Patient post
#
#
#
# VCF post
