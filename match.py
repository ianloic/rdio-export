# from: http://stackoverflow.com/questions/2460177/edit-distance-in-python
import re

import unicodedata


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
