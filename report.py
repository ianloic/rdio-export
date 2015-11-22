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
                <div>
                    <p>
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
        self.f.write('''
                <div class="pure-g track %s">
                    <div class="pure-u-4-24 score">%d</div>
                    <div class="pure-u-10-24 rdio">%s</div>
                    <div class="pure-u-10-24 play">%s</div>
                </div class="pure-g">
        ''' % (match_class, match.match, match.rdio.html(), play))

    def close(self):
        self.f.write('''
            <script>
                $('#show').change(function() {
                    if ($(this).is(':checked')) {
                        $('.match-ok').show(0);
                    } else {
                        $('.match-ok').hide(0);
                    }
                })
            </script>
            </body>
        </html>
        ''')
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
