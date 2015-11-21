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

    def favorite_tracks(self, user_key):
        """
        A generator for a the tracks a user has favorited.
        """
        start = 0
        while True:
            faves = self.call('getFavorites', user=user_key, types='tracksAndAlbums', extras='tracks', start=start)
            if len(faves):
                start += len(faves)
            else:
                break

            for fave in faves:
                if fave['type'] == 'a':
                    for track in fave['tracks']:
                        yield track
                elif fave['type'] == 't':
                    yield fave

