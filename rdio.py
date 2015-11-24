# Copyright 2015 Ian McKellar <http://ian.mckellar.org/>
#
# This file is part of Rdio Export.
#
# Rdio Export is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Rdio Export is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Rdio Export.  If not, see <http://www.gnu.org/licenses/>.

import requests
import time
from match import Track

CLIENT_ID = 'e3b4yf4qlfaczasrh5y2t7wr74'
CLIENT_SECRET = 'Gtwwvr2toSey0O_slclZUw'


class RdioTrack(Track):
    def __init__(self, rdio_track):
        Track.__init__(self,
                       id=rdio_track['key'],
                       url=rdio_track['shortUrl'],
                       name=rdio_track['name'],
                       artist=rdio_track['artist'],
                       album=rdio_track['album'],
                       album_artist=rdio_track.get('albumArtist'),
                       duration=rdio_track['duration'],
                       track_num=rdio_track['trackNum'],
                       available=rdio_track['canStream'])


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
        retries = 5
        while retries:
            r = requests.post('https://services.rdio.com/api/1/', data=args,
                              headers={'Authorization': 'Bearer ' + self.bearer_token})
            if r.status_code != 408:
                return r.json()['result']
            else:
                retries -= 1
                time.sleep(3)
        raise Exception('Rdio API call "%s" failed' % method)

    def get_one(self, key, extras=''):
        return self.call('get', keys=key, extras=extras)[key]

    @staticmethod
    def playlist_tracks(playlist):
        """
        Turn an Rdio API playlist response into a list of Tracks that can be matched.
        :param playlist: a playlist from the Rdio service that includes the 'tracks' extra
        :return: an array of RdioTracks for the playlist's tracks
        """
        return [RdioTrack(t) for t in playlist['tracks']]

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
                        yield RdioTrack(track)
                elif fave['type'] == 't':
                    yield RdioTrack(fave)

