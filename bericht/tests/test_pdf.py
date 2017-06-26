from bericht.html import HTMLParser
from bericht.pdf import PDFStreamer


def html_gen():
    yield '<p>first '
    for i in range(1, 3):
        yield 'hello world {}</p><p>'.format(i)
    yield 'end</p>'
    #yield '<table>'
    #for i in range(1, 3):
    #    yield '<tr><td>row {} col 1</td><td>row {} col 2</td></tr>'.format(i, i)
    #yield '</table>'
    yield '<p>last p</p>'


def test():
    with open('test.pdf', 'wb') as pdf:
        for chunk in PDFStreamer(HTMLParser(html_gen())):
            print(chunk)
            pdf.write(chunk)

test()
