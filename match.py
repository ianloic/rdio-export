# from: http://stackoverflow.com/questions/2460177/edit-distance-in-python
import re

import unicodedata

import sys


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


class TrackMatch:
    def __init__(self, rdio_track, play_track, play_music):
        self.rdio = rdio_track['shortUrl']
        self.canStream = rdio_track['canStream']
        self.name = rdio_track['name']
        self.artist = rdio_track['artist']
        self.album = rdio_track['album']
        if play_track:
            self.play = play_music.track_url(play_track)
            self.play_id = play_track['nid']
            self.match = play_track['match']
        else:
            self.play = ''
            self.play_id = None
            self.match = 0

    def good(self):
        return self.match >= 75

    def failed(self):
        return self.match <= 50

    def bad(self):
        return not self.good() and not self.failed()

    def __str__(self):
        if self.canStream:
            stream = '+'
        else:
            stream = '-'
        return u'%03d %-24s %s %s %s / %s / %s' % (
            self.match,
            self.rdio,
            stream,
            self.play,
            self.name,
            self.artist,
            self.album,
        )


def match_tracks(rdio_tracks, num_tracks, play_music, logfile):
    count = 0
    good = 0
    bad = 0
    failed = 0

    for rdio_track in rdio_tracks:
        match = TrackMatch(rdio_track, play_music.match_track(rdio_track), play_music)
        logfile.write(unicode(match))
        logfile.write('\n')
        logfile.flush()
        yield match
        if match.good():
            good += 1
        elif match.bad():
            bad += 1
        else:
            failed += 1
        count += 1
        percentage = int(100 * count / float(num_tracks))
        sys.stdout.write(' % 6d/%d scanned % 2d%%. %d good, %d bad, %d failed\r' % (
            count, num_tracks, percentage, good, bad, failed))
        sys.stdout.flush()
    sys.stdout.write('\n')
    sys.stdout.flush()
