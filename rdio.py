import requests

CLIENT_ID = 'p4e6qtaqprct7h2c3y3qxhobmm'
CLIENT_SECRET = 'ZQpKs4rAen7eKMTwTX9IXg'


class Rdio:
    def __init__(self, bearer_token=None):
        self.bearer_token = bearer_token
        if bearer_token is None:
            self.get_client_bearer_token()

    def get_client_bearer_token(self):
        r = requests.post('https://services.rdio.com/oauth2/token', data={
            'grant_type': 'client_credentials'
        }, auth=(CLIENT_ID, CLIENT_SECRET))
        self.bearer_token = r.json()['access_token']

    def call(self, method, **args):
        args['method'] = method
        r = requests.post('https://services.rdio.com/api/1/', data=args,
                          headers={'Authorization': 'Bearer ' + self.bearer_token})
        return r.json()['result']

    def get_one(self, key, extras=''):
        return self.call('get', keys=key, extras=extras)[key]
