import re
import sys
import time

sys.path.insert(0, 'lib/')

from gmusicapi import Mobileclient, CallFailure
from match import Track, remove_parens

GOOGLE_USERNAME = 'import@mckellar.org'
# GOOGLE_PASSWORD = 'Piah5ohC'
GOOGLE_PASSWORD = 'ckwykmfopdvqwlfg'
GOOGLE_ANDROID_ID = '10a231a66f301274'

MAX_QUERY_LENGTH = 120


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


def replace_non_alphanumeric(s):
    return re.sub(r'[^A-Za-z0-9 ]', ' ', s)


class PlayMusic():
    def __init__(self):
        self.client = Mobileclient()
        self.client.login(GOOGLE_USERNAME, GOOGLE_PASSWORD, GOOGLE_ANDROID_ID)

    def is_authenticated(self):
        return self.client.is_authenticated()

    @staticmethod
    def track_url(play_track):
        return 'https://play.google.com/music/m/%s' % play_track['nid']

    @staticmethod
    def playlist_url(playlist_id):
        return 'https://play.google.com/music/playlist/%s' % playlist_id

    def __search_tracks(self, *query_items):
        query = ' '.join(query_items)
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

        retries = 5
        response = None
        while retries and not response:
            retries -= 1
            try:
                response = self.client.search_all_access(query)
            except CallFailure, e:
                if not retries:
                    raise e
                # sleep for two seconds before retrying
                time.sleep(2)
        return [PlayTrack(song['track']) for song in response['song_hits']]

    def tracks_matching(self, rdio_track):
        """
        :type rdio_track Track
        """
        # search for matching tracks
        return (self.__search_tracks(rdio_track.name,
                                     rdio_track.artist,
                                     rdio_track.album) +
                self.__search_tracks(remove_parens(rdio_track.name),
                                     remove_parens(rdio_track.artist),
                                     remove_parens(rdio_track.album)) +
                self.__search_tracks(remove_parens(rdio_track.name),
                                     remove_parens(rdio_track.artist)) +
                self.__search_tracks(replace_non_alphanumeric(rdio_track.name),
                                     replace_non_alphanumeric(rdio_track.artist),
                                     replace_non_alphanumeric(rdio_track.album)))

    def create_playlist(self, name, description, play_track_ids):
        playlist_id = self.client.create_playlist(name, description)
        self.client.add_songs_to_playlist(playlist_id, play_track_ids)
        return playlist_id

    def add_track(self, play_id):
        self.client.add_aa_track(play_id)

    def get_all_playlists(self):
        return self.client.get_all_playlists()
