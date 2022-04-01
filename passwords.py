import os

class alissa_prod:
    username = os.environ.get('ALISSA_USERNAME')
    password = os.environ.get('ALISSA_PASSWORD')
    token_url = os.environ.get('ALISSA_TOKEN_URL')
    bench_url = os.environ.get('ALISSA_BENCH_URL')

class alissa_test:
    username = os.environ.get('ALISSA_TEST_USERNAME')
    password = os.environ.get('ALISSA_TEST_PASSWORD')
    token_url = os.environ.get('ALISSA_TEST_TOKEN_URL')
    bench_url = os.environ.get('ALISSA_TEST_BENCH_URL')
