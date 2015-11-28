#!/usr/bin/env python

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

import argparse
import getpass
import re
import sys

from match import match_tracks
from playmusic import PlayMusic
from rdio import Rdio
from report import Report

parser = argparse.ArgumentParser(description='Export playlists and favorites from Rdio to Play Music')
parser.add_argument('rdio_username', help='username on Rdio')
parser.add_argument('google_email', help='Google account email address')
args = parser.parse_args()

google_password = getpass.getpass('%s password:' % args.google_email)

print 'Connecting to Rdio...'
rdio = Rdio()
print 'Connecting to Play Music...'
pm = PlayMusic(args.google_email, google_password)
if not pm.is_authenticated():
    print 'Google login failed.'
    sys.exit(1)


def migrate_playlist(user_key, playlist):
    print u'\nMigrating playlist: %s' % playlist['name']
    name = playlist['name']
    if playlist['ownerKey'] != user_key:
        name += u' (by %s)' % playlist['owner']
    description = u'Imported from Rdio playlist %s\n' % playlist['shortUrl']
    play_track_ids = []
    failed = []
    tracks = rdio.playlist_tracks(playlist)
    if tracks is None:
        print u'Can\'t get tracks for playlist "%s" - it might be private.' % playlist['name']
        return
    with Report('playlist-%s.html' % playlist['key'], name) as report:
        for match in match_tracks(tracks, len(tracks), pm):
            report.add_match(match)
            if match.matched():
                play_track_ids.append(match.play.id)
            else:
                failed.append(match)
        if failed:
            description += 'Failed to import: '
            for match in failed:
                description += u'%s (%s / %s / %s)' % (
                    match.rdio.url, match.rdio.name, match.rdio.artist, match.rdio.album)
        playlist_id = pm.create_playlist(name, description, play_track_ids)
        print u'Imported to %s' % pm.playlist_url(playlist_id)


def migrate_playlists(rdio_username):
    print 'Finding playlists...'
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

    # Find already imported playlists's Rdio URL.
    imported = frozenset([m.groups()[0] for m in
                          [re.match(r'Imported from Rdio playlist (http://rd.io/x/.*?/)', p['description'])
                           for p in pm.get_all_playlists() if 'description' in p]
                          if m])

    for playlist in playlists.values():
        if playlist['shortUrl'] in imported:
            print('Already imported playlist %s. Delete it from Play Music if you want to re-import it.' %
                  playlist['name'])
            continue
        migrate_playlist(user_key, playlist)


def migrate_favorites(rdio_username):
    user = rdio.call('findUser', vanityName=rdio_username, extras='trackCount')
    print 'Migrating %(trackCount)d favorites for %(firstName)s %(lastName)s' % user

    rdio_tracks = rdio.favorite_tracks(user['key'])
    with Report('favorites.html', "%(firstName)s %(lastName)s's Favorites" % user) as report:
        matched_tracks = match_tracks(rdio_tracks, user['trackCount'], pm)
        for match in matched_tracks:
            report.add_match(match)
            if match.matched():
                pm.add_track(match.play.id)


migrate_playlists(args.rdio_username)
migrate_favorites(args.rdio_username)
