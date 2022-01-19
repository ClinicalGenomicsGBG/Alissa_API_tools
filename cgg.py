import passwords

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

        self.is_valid_token(self._token)
        return self._token

    def is_valid_token(self) -> bool:
        return self.session.authorized
    
def main():
    oauth2_client = OAuth2Client()
    oauth2_client.fetch_token()
    print(oauth2_client._token)
    print(oauth2_client.session.authorized)
   
if __name__ == '__main__':
    main()
