from bericht.html import HTMLParser
from bericht.pdf import PDFStreamer


def html_gen():
    yield '<p>first ' + ' some really long sentance' * 0
    for i in range(1, 3):
        yield 'hello world {}</p><p>'.format(i)
    yield 'end</p>'
    yield '<table>'
    yield '<colgroup>'
    yield '<col width="0*">row 99 col 99</col>'
    yield '<col width="3*"></col>'
    yield '<col width="1*"></col>'
    yield '</colgroup>'
    yield '<thead>'
    yield '<tr><td><p>name</td><td><p>description</td><td><p>row</td>'
    yield '<tr><td></td><td><p>multi row header</td><td></td>'
    yield '</thead>'
    for i in range(1, 30):
        yield '<tr><td><p>row {} col 1</p></td><td><p>row {} col 2 {}</p></td><td><p>{}</p></td></tr>'.format(i, i, 'blah blah' * 10, i)
    yield '</table>'
    yield '<p>last p</p>'


def test():
    with open('test.pdf', 'wb') as pdf:
        for chunk in PDFStreamer(HTMLParser(html_gen())):
            print(chunk)
            pdf.write(chunk)

test()
