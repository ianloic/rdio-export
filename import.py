#!/usr/bin/env python

import codecs
import sys

from playmusic import PlayMusic
from rdio import Rdio

print 'Connecting to Rdio...'
rdio = Rdio()
print 'Connecting to Play Music...'
pm = PlayMusic()


class Track:
    def __init__(self, rdio_track, play_track):
        self.rdio = rdio_track['shortUrl']
        self.canStream = rdio_track['canStream']
        self.name = rdio_track['name']
        self.artist = rdio_track['artist']
        self.album = rdio_track['album']
        if play_track:
            self.play = pm.track_url(play_track)
            self.play_id = play_track['nid']
            self.match = play_track['match']
        else:
            self.play = ''
            self.play_id = ''
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
        return u'%03d %24s %s %s %s / %s / %s' % (
            self.match,
            self.rdio,
            stream,
            self.play,
            self.name,
            self.artist,
            self.album,
        )


def migrate_favorites(rdio_username):
    favorites = []
    good = 0
    bad = 0
    failed = 0
    logfile = codecs.open('favorites-log.txt', 'wt', 'utf-8')
    user = rdio.call('findUser', vanityName=rdio_username, extras='trackCount')
    print 'Migrating %(trackCount)d favorites for %(firstName)s %(lastName)s' % user
    start = 0
    while True:
        faves = rdio.call('getFavorites', user='s13', types='tracksAndAlbums', extras='tracks', start=start)
        if len(faves):
            start += len(faves)
        else:
            break

        rdio_tracks = []
        for fave in faves:
            if fave['type'] == 'a':
                rdio_tracks.extend(fave['tracks'])
            elif fave['type'] == 't':
                rdio_tracks.append(fave)
            else:
                print 'unexpected favorite:'
                from pprint import pprint

                pprint(fave)
                sys.exit(1)

        for rdio_track in rdio_tracks:
            # print "%(name)s / %(artist)s / %(album)s" % rdio_track
            track = Track(rdio_track, pm.match_track(rdio_track))
            logfile.write(unicode(track))
            logfile.write('\n')
            logfile.flush()
            favorites.append(track)
            if track.good():
                good += 1
            elif track.bad():
                bad += 1
            else:
                failed += 1
            count = len(favorites)
            percentage = int(100 * count / float(user['trackCount']))
            sys.stdout.write(' % 6d/%d scanned % 2d%%. %d good, %d bad, %d failed\r' % (
                count, user['trackCount'], percentage, good, bad, failed))
            sys.stdout.flush()


migrate_favorites('ian')
