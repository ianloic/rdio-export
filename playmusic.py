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

import hashlib
import sys
import time

sys.path.insert(0, 'lib/')
sys.path.insert(0, 'gmusicapi-module/')

from gmusicapi import Mobileclient
from match import Track

MAX_QUERY_LENGTH = 120

RETRIES = 5


class PlayTrack(Track):
    def __init__(self, play_track):
        Track.__init__(self,
                       id=play_track['nid'],
                       url=PlayMusic.track_url(play_track),
                       name=play_track['title'],
                       artist=play_track['artist'],
                       album=play_track['album'],
                       album_artist=play_track['albumArtist'],
                       duration=int(play_track['durationMillis']) / 1000,
                       track_num=play_track['trackNumber'])


class PlayMusic():
    def __init__(self, google_username, google_password):
        self.client = Mobileclient(validate=False)
        # generate a stable, unique android id
        h = hashlib.sha256()
        h.update(google_username)
        android_id = h.hexdigest()[:16]
        self.client.login(google_username, google_password, android_id)

    def is_authenticated(self):
        return self.client.is_authenticated()

    @staticmethod
    def track_url(play_track):
        return 'https://play.google.com/music/m/%s' % play_track['nid']

    @staticmethod
    def playlist_url(playlist_id):
        return 'https://play.google.com/music/playlist/%s' % playlist_id

    def search_tracks(self, query):
        if len(query) >= MAX_QUERY_LENGTH:
            # long queries don't work for some reason
            # for example "The Moderately Talented Yet Attractive Young Woman vs. The Exceptionally Talented Yet Not
            # So Attractive Middle Aged Man / Sun Kil Moon / Among The Leaves"
            parts = query.split(' ')
            query = parts.pop(0)
            for part in parts:
                if len(query) + 1 + len(part) > MAX_QUERY_LENGTH:
                    break
                query += ' ' + part

        retries = RETRIES
        response = None
        while retries and not response:
            retries -= 1
            try:
                response = self.client.search_all_access(query)
            except Exception, e:
                if not retries:
                    raise e
                # sleep for two seconds before retrying
                time.sleep(2)
        return [PlayTrack(song['track']) for song in response['song_hits']]

    def create_playlist(self, name, description, play_track_ids):
        playlist_id = self.client.create_playlist(name, description)
        self.client.add_songs_to_playlist(playlist_id, play_track_ids)
        return playlist_id

    def add_track(self, play_id):
        retries = RETRIES
        while retries >= 0:
            retries -= 1
            try:
                self.client.add_aa_track(play_id)
                break
            except Exception, e:
                if not retries:
                    raise e
                time.sleep(2)

    def get_all_playlists(self):
        return self.client.get_all_playlists()
