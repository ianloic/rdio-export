#!/usr/bin/env python

import codecs
import sys

from match import match_tracks
from playmusic import PlayMusic
from rdio import Rdio

print 'Connecting to Rdio...'
rdio = Rdio()
print 'Connecting to Play Music...'
pm = PlayMusic()
if not pm.is_authenticated():
    print 'Google login failed.'
    sys.exit(1)


def migrate_playlist(user_key, playlist, logfile):
    print u'\nMigrating playlist: %s' % playlist['name']
    logfile.write(u'Playlist: %s\n' % playlist['name'])
    name = playlist['name']
    if playlist['ownerKey'] != user_key:
        name += u' (by %s)' % playlist['owner']
    description = u'Imported from Rdio playlist %s\n' % playlist['shortUrl']
    play_track_ids = []
    failed = []
    for match in match_tracks(playlist['tracks'], len(playlist['tracks']), pm, logfile):
        if match.play_id:
            play_track_ids.append(match.play_id)
        else:
            failed.append(match)
    if failed:
        description += 'Failed to import: '
        for match in failed:
            description += u'%s (%s / %s / %s)' % (match.rdio, match.name, match.artist, match.album)
    playlist_id = pm.create_playlist(name, description, play_track_ids)
    print u'Imported to %s' % pm.playlist_url(playlist_id)


def migrate_playlists(rdio_username):
    logfile = codecs.open('playlists-log.txt', 'wt', 'utf-8')
    user = rdio.call('findUser', vanityName=rdio_username, extras='trackCount')
    user_key = user['key']
    playlists = {}
    for kind in ('owned', 'collab', 'favorites', 'subscribed'):
        start = 0
        while True:
            pls = rdio.call('getUserPlaylists', user=user_key, kind=kind, extras='tracks,ownerKey', start=start)
            if not pls:
                break
            start += len(pls)
            for pl in pls:
                playlists[pl['key']] = pl

    for playlist in playlists.values():
        migrate_playlist(user_key, playlist, logfile)


def migrate_favorites(rdio_username):
    logfile = codecs.open('favorites-log.txt', 'wt', 'utf-8')
    user = rdio.call('findUser', vanityName=rdio_username, extras='trackCount')
    print 'Migrating %(trackCount)d favorites for %(firstName)s %(lastName)s' % user
    start = 0

    rdio_tracks = rdio.favorite_tracks(user['key'])
    matched_tracks = match_tracks(rdio_tracks, user['trackCount'], pm, logfile)
    for match in matched_tracks:
        if match.play_id and match.good():
            pm.add_track(match.play_id)


#migrate_favorites('ian')
migrate_playlists('ian')
