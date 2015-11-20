import re
import time
import unicodedata

from gmusicapi import Mobileclient, CallFailure

GOOGLE_USERNAME = 'import@mckellar.org'
GOOGLE_PASSWORD = 'Piah5ohC'
GOOGLE_ANDROID_ID = '10a231a66f301274'


# from: http://stackoverflow.com/questions/2460177/edit-distance-in-python
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def remove_parens(s):
    """
    :param s: a string
    :return: that string with everything within () or [] removed
    """
    return re.sub(r'\[.*?\]', '', re.sub(r'\(.*?\)', '', s))


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def only_alphanumeric(s):
    return re.sub(r'[^A-Za-z0-9]', '', s)


def string_match(a, b):
    """

    :param a: string
    :param b: string
    :return:
    """
    # exact match
    if a == b:
        return 100

    # from here on out, everything is case insensitive without accents
    a = remove_accents(a.lower())
    b = remove_accents(b.lower())

    # case insensitive match
    if a == b:
        return 95

    # match removing non-alphanumeric characters
    if only_alphanumeric(a) == only_alphanumeric(b):
        return 80

    # match removing things between () and []
    if remove_parens(a) == remove_parens(b):
        return 70

    # Edit distance
    # TODO: weight by length?
    return 100 / (levenshteinDistance(a, b) + 1)


def print_match(a, b):
    print('%03d\t%s\t%s' % (string_match(a, b), a, b))


def average(numbers):
    # TODO: weight averages?
    return sum(numbers) / len(numbers)


def delta(a, b):
    return 100 / (abs(a - b) + 1)


def track_match(play_track, rdio_track):
    percentages = [
        string_match(play_track['title'], rdio_track['name']),
        string_match(play_track['artist'], rdio_track['artist']),
        string_match(play_track['album'], rdio_track['album']),
        delta(int(play_track['trackNumber']), rdio_track['trackNum']),
    ]
    if rdio_track['duration']:
        percentages.append(delta(int(play_track['durationMillis']) / 1000, rdio_track['duration']))
    if 'albumArtist' in rdio_track:
        percentages.append(string_match(play_track['albumArtist'], rdio_track['albumArtist']))
    return average(percentages)


def best_match(play_tracks, rdio_track):
    # for each track, calculate match percentage
    for play_track in play_tracks:
        play_track['match'] = track_match(play_track, rdio_track)
    # sort by match
    play_tracks.sort(lambda a, b: cmp(a['match'], b['match']))
    # chose the highest match
    return play_tracks[-1]


class PlayMusic():
    def __init__(self):
        self.client = Mobileclient()
        self.client.login(GOOGLE_USERNAME, GOOGLE_PASSWORD, GOOGLE_ANDROID_ID)

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

        return None
