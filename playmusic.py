import time

from gmusicapi import Mobileclient, CallFailure

from match import best_match, remove_parens

GOOGLE_USERNAME = 'import@mckellar.org'
# GOOGLE_PASSWORD = 'Piah5ohC'
GOOGLE_PASSWORD = 'ckwykmfopdvqwlfg'
GOOGLE_ANDROID_ID = '10a231a66f301274'


# Failures:
#  Only Lovers Left Alive (Original Motion Picture Soundtrack)






class PlayMusic():
    def __init__(self):
        self.client = Mobileclient()
        self.client.login(GOOGLE_USERNAME, GOOGLE_PASSWORD, GOOGLE_ANDROID_ID)

    def is_authenticated(self):
        return self.client.is_authenticated()

    @staticmethod
    def track_url(play_track):
        return 'https://play.google.com/music/m/%s' % play_track['nid']

    def __search_tracks(self, *query_items):
        query = ' '.join(query_items)
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
        return [song['track'] for song in response['song_hits']]

    def match_track(self, rdio_track):
        # search for matching tracks
        play_tracks = self.__search_tracks(rdio_track['name'],
                                           rdio_track['artist'],
                                           rdio_track['album'])
        if play_tracks:
            return best_match(play_tracks, rdio_track)

        # try without the () [] terms
        play_tracks = self.__search_tracks(remove_parens(rdio_track['name']),
                                           remove_parens(rdio_track['artist']),
                                           remove_parens(rdio_track['album']))
        if play_tracks:
            return best_match(play_tracks, rdio_track)
        # how about without the album name at all
        play_tracks = self.__search_tracks(remove_parens(rdio_track['name']),
                                           remove_parens(rdio_track['artist']))
        if play_tracks:
            return best_match(play_tracks, rdio_track)

        # TODO: remove non alpha & space (for poorly HTML encoded Le VICE, u-Ziq)
        # TODO: handle long track names by searching only for artist & album?

        return None

    def create_playlist(self, name, description, play_track_ids):
        playlist_id = self.client.create_playlist(name, description)
        self.client.add_songs_to_playlist(playlist_id, play_track_ids)
        return playlist_id
