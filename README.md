Rdio Export to Google Play Music
================================

Export your Rdio favorites and playlists to Google Play Music.


Requirements
------------
 * An Rdio account.
 * A Google Play Music account with an [Unlimited subscription](https://support.google.com/googleplay/answer/3139566).
 * Python on a UNIX-like computer. I use Debian GNU/Linux. A Mac might work.

Google Authentication
---------------------
If you use 2-Step Verification (and you should) then you need to 
[create](https://security.google.com/settings/security/apppasswords) an /App password/ rather than using your normal 
Google password.

Setup
-----
Install the right version of the gmusicapi module by running:

    git submodule update --init

and its dependencies by running

    pip install --user -r gmusicapi-module/requirements.txt

Running
-------
To import all your public Rdio playlists and favorites into your Play Music account run with your Rdio username and 
Google account.

    python rdio-export.py rdio_username yourname@gmail.com

Then enter your Google App password, sit back and let the program do its thing. It can take a while.

After it runs there will be HTML reports generated for your imported favorites (`favorites.html`) and for each 
playlist (`playlist-*.html`). Take a look to make sure the tool did the right thing with your data.

Matching
--------
This script does its best to match the tracks from Rdio to those on Google Play Music. Sometimes it will get
things wrong. You should look through the HTML reports to make sure it did the right thing. It's also slow.
For each Rdio track the Google Play Music catalog will be searched at least a couple of times to make sure that
the best match has been found. It tries to avoid picking "karaoke" or instrumental cover tracks if possible.
