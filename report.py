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

import codecs
from xml.sax.saxutils import escape

# TODO: generate an overview reports.html and open it after the import completes


class Report:
    def __init__(self, filename, title):
        self.f = codecs.open(filename, 'wt', encoding='utf-8')
        self.f.write('''
        <html>
            <head>
                <title>%s</title>
                <link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.6.0/pure-min.css">
                <link rel="stylesheet" href="report.css">
                <script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
            </head>
            <body>
                <h1>%s</h1>
                <div>
                    <input type="checkbox" id="show">
                    <label for="show">Show good matches</label>
                </div>
                <script>
                    $('#show').change(function() {
                        if ($(this).is(':checked')) {
                            $('.match-ok').show(0);
                        } else {
                            $('.match-ok').hide(0);
                        }
                    })
                </script>
                <div>
                    <p><b>Legend</b></p>
                    <dl>
                        <dt class="green">green</dt>
                        <dd>A good, confident match.</dd>
                        <dt class="yellow">yellow</dt>
                        <dd>A marginal match, but imported optimistically</dd>
                        <dt class="red">red</dt>
                        <dd>No match or a bad match, not imported</dd>
                        <dt class="unavailable">strikethrough</dt>
                        <dd>The track wasn't available on Rdio so might not be streamable on Play either</dd>
                    </dl>
                </div>
                <div class="pure-g header">
                    <div class="pure-u-4-24">Score</div>
                    <div class="pure-u-10-24">Rdio</div>
                    <div class="pure-u-10-24">Play Music</div>
                </div>
        ''' % (escape(title), escape(title)))

    def add_match(self, match):
        """
        :type match match.TrackMatch
        """
        if match.play:
            play = match.play.html()
        else:
            play = ''
        if match.matched():
            if match.match < 50:
                match_class = 'match-marginal'
            else:
                match_class = 'match-ok'
        else:
            match_class = 'match-bad'
        if not match.rdio.available:
            match_class += ' unavailable'
        self.f.write('''
                <div class="pure-g track %s">
                    <div class="pure-u-4-24 score">%d</div>
                    <div class="pure-u-10-24 rdio">%s</div>
                    <div class="pure-u-10-24 play">%s</div>
                </div class="pure-g">
        ''' % (match_class, match.match, match.rdio.html(), play))

    def close(self):
        self.f.write('''
            </body>
        </html>
        ''')
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
