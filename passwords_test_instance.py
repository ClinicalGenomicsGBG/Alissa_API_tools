import os

class alissa:
    username = os.environ.get('ALISSA_TEST_USERNAME')
    password = os.environ.get('ALISSA_TEST_PASSWORD')
    token_url = os.environ.get('ALISSA_TEST_TOKEN_URL')
    bench_url = os.environ.get('ALISSA_TEST_BENCH_URL')
