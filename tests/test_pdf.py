from bericht.html import HTMLParser
from bericht.pdf import PDFStreamer


def html_gen():
    yield '<p>begin hello world<br>'
    for i in range(1, 3):
        yield '{} hello world<br>'.format(i)
    yield 'end hello world</p>'
    yield '<p>new paragraph</p>'
    yield """<table>
  <colgroup>
    <col width="1*" />
    <col width="0*">April 6, 2017</col>
  </colgroup>
  <tr>
    <td><p>Angebot (2.1)</p></td>
    <td><p>April 6, 2017</p></td>
  </tr>
</table>"""
    yield '<p>now for big table</p>'
    yield '<p>now for big table</p>'
    yield '<p>now for big table</p>'
    yield '<table>'
    yield '<colgroup>'
    yield '<col width="0*">row 99 col 99</col>'
    yield '<col width="3*">'
    yield '<col width="1*">'
    yield '</colgroup>'
    yield '<thead>'
    yield '<tr><td><p>name</td><td><p>description</td><td><p>row</td></tr>'
    yield '<tr><td></td><td colspan="2"><p>multi row header</td></tr>'
    yield '</thead>'
    #yield '<tfoot>'
    #yield '<tr><td colspan="3"><p>the footer</td></tr>'
    #yield '</tfoot>'
    for i in range(1, 30):
        yield '<tr><td><p>row {} col 1</p></td><td><p>row {} col 2 {}</p></td><td><p>{}</p></td></tr>'.format(i, i, 'blah blah' * 11, i)
    yield '</table>'
    yield '<p>last p</p>'


def test():
    with open('test.pdf', 'wb') as pdf:
        for chunk in PDFStreamer(HTMLParser(html_gen())):
            print(chunk)
            pdf.write(chunk)

test()
