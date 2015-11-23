import re
import sys
import unicodedata

COVERS = {'Vitamin String Quartet'}


class Track:
    def __init__(self, id, url, name, artist, album, album_artist, duration, track_num, available=True):
        self.id = id
        self.url = url
        self.name = name
        self.artist = artist
        self.album = album
        self.album_artist = album_artist
        self.duration = duration
        self.track_num = track_num
        self.available = available

    def __str__(self):
        return '%s / %s / %s <%s>' % (self.name, self.artist, self.album, self.url)

    def html(self):
        return ('<a href="%s"><span class="name">%s</span> / <span class="artist">%s</span> / ' +
                '<span class="album">%s</span></a>') % (self.url, self.name, self.artist, self.album)


def levenshtein_distance(s1, s2):
    # from: http://stackoverflow.com/questions/2460177/edit-distance-in-python
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


def replace_non_alphanumeric(s):
    return re.sub(r'[^A-Za-z0-9\. ]', ' ', s)


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
    return 100 / (levenshtein_distance(a, b) + 1)


def average(numbers):
    # TODO: weight averages?
    return sum(numbers) / len(numbers)


def delta(a, b):
    return 100 / (abs(a - b) + 1)


def track_match(play_track, rdio_track):
    """
    :type play_track Track
    :type rdio_track Track
    :rtype int
    """
    if not play_track:
        return 0
    # Exclude artists that specialize in covers, unless they were actually requested
    if play_track.artist != rdio_track.artist and play_track.artist in COVERS:
        return 0
    # TODO: exclude 'Karaoke' tracks (unless that's what we had)
    percentages = [
        string_match(play_track.name, rdio_track.name),
        string_match(play_track.artist, rdio_track.artist),
        string_match(play_track.album, rdio_track.album),
        delta(int(play_track.track_num), rdio_track.track_num),
    ]
    if rdio_track.duration and play_track.duration:
        percentages.append(delta(play_track.duration, rdio_track.duration))
    if rdio_track.album_artist and play_track.album_artist:
        percentages.append(string_match(play_track.album_artist, rdio_track.album_artist))
    return average(percentages)


class TrackMatch:
    def __init__(self, rdio_track, play_track):
        """
        :type rdio_track: Track
        :type play_track: Track
        """
        self.rdio = rdio_track
        self.play = play_track
        self.match = track_match(play_track, rdio_track)

    def __cmp__(self, other):
        return cmp(self.match, other.match)

    def matched(self):
        return self.match > 20

    def confident(self):
        return self.match > 50

    def __str__(self):
        if self.rdio.available:
            stream = '+'
        else:
            stream = '-'
        return u'%03d %s %s %s' % (self.match, stream, self.rdio, self.play)


def search_queries(track):
    """
    Generate search queries for a track.
    :param track:
    :type track Track
    :return: a search query string
    :rtype List[string]
    """
    return (' '.join((track.name,
                      track.artist,
                      track.album)),
            ' '.join((remove_parens(track.name),
                      remove_parens(track.artist),
                      remove_parens(track.album))),
            ' '.join((remove_parens(track.name),
                      remove_parens(track.artist))),
            ' '.join((replace_non_alphanumeric(track.name),
                      replace_non_alphanumeric(track.artist),
                      replace_non_alphanumeric(track.album))))


def match_tracks(rdio_tracks, num_tracks, play_music):
    """
    :type rdio_tracks List[rdio.RdioTrack]
    :type num_tracks int
    :type play_music playmusic.PlayMusic
    """
    count = 0
    matched = 0
    unmatched = 0
    unmatched_missing = 0

    for rdio_track in rdio_tracks:
        matches = []
        # Try each kind of query until we get a confident match
        for query in search_queries(rdio_track):
            matches.extend([TrackMatch(rdio_track, play_track) for play_track in play_music.search_tracks(query)])
            matches.sort(reverse=True)
            if matches and matches[0].confident():
                break
        if matches:
            match = matches[0]
        else:
            match = TrackMatch(rdio_track, None)
        yield match
        if match.matched():
            matched += 1
        elif match.rdio.available:
            unmatched += 1
        else:
            unmatched_missing += 1
        count += 1
        percentage = int(100 * count / float(num_tracks))
        sys.stdout.write(' % 6d/%d scanned % 2d%%. %d matched, %d unmatched, %d unmatched but unavailable on Rdio\r' % (
            count, num_tracks, percentage, matched, unmatched, unmatched_missing))
        sys.stdout.flush()
    sys.stdout.write('\n')
    sys.stdout.flush()
