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
Install the required dependencies by running:

    pip install --user -r requirements.txt

Running
-------
To import all your public Rdio playlists and favorites into your Play Music account run with your Rdio username and 
Google account.

    python rdio-export.py rdio_username yourname@gmail.com

Then enter your Google App password, sit back and let the program do its thing. It can take a while.

After it runs there will be HTML reports generated for your imported favorites (`favorites.html`) and for each 
playlist (`playlist-*.html`). Take a look to make sure the tool did the right thing with your data.
