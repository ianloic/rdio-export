import codecs
from xml.sax.saxutils import escape


class Report:
    def __init__(self, filename, title):
        self.f = codecs.open(filename, 'wt', encoding='utf-8')
        self.f.write('''
        <html>
            <head>
                <title>%s</title>
                <link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.6.0/pure-min.css">
                <link rel="stylesheet" href="report.css">
            </head>
            <body>
                <h1>%s</h1>
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
        self.f.write('''
                <div class="pure-g track score-%d">
                    <div class="pure-u-4-24 score">%d</div>
                    <div class="pure-u-10-24 rdio">%s</div>
                    <div class="pure-u-10-24 play">%s</div>
                </div class="pure-g">
        ''' % (match.match / 10, match.match, match.rdio.html(), play))

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
