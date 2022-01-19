import os

class alissa:
    username = os.environ.get('ALISSA_USERNAME')
    password = os.environ.get('ALISSA_PASSWORD')
    token_url = os.environ.get('ALISSA_TOKEN_URL')
    base_url = os.environ.get('ALISSA_BASE_URL')
