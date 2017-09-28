from bericht.pdf import PDFDocument
from utils import BaseTestCase


TABLE_HTML = """
<table>
  <colgroup>
    <col width="0*">
    <col width="1*">
    <col width="0*">
    <col width="0*">
  <thead>
    <tr>
      <td>code
      <td>name
      <td>price
      <td>total
  </thead>
  <tfoot>
    <tr><td colspan="4">footer<br>line
  </tfoot>
  <tr>
    <td>1
    <td>First Item
    <td>10.00
    <td>10.00
  <tr>
    <td>2
    <td>{}
    <td>15.00
    <td>25.00
""".format('Second Long Item '*1000)


class TestTable(BaseTestCase):

    def test_only_returns_rows(self):
        nodes = list(self.parse(TABLE_HTML))
        self.assertEqual(nodes[0].tag, 'tr')
        self.assertEqual(nodes[1].tag, 'tr')
        self.assertEqual(len(nodes), 2)

    def test_minimal_tags(self):
        nodes = self.parse(TABLE_HTML)
        row1, row2 = nodes
        page = PDFDocument(nodes.css).add_page()
        row1.wrap(page, page.available_width)
        row1.draw(page, page.x, page.y)


class TestCells(BaseTestCase):

    def get_cell(self, content):
        return next(iter(self.parse(
            """<table><tr><td>{}</td></tr></table>""".format(content)
        ))).children[0]

    def get_cells(self, content):
        return next(iter(self.parse(
            """<table><tr>{}</tr></table>""".format(''.join('<td>'+td+'<td>' for td in content))
        ))).children

    def test_blank_cell(self):
        cell = self.get_cell('')
        self.assertEqual(cell.children, [])

    def test_implicit_paragraph(self):
        cell = self.get_cell('hello world')
        self.assertEqual(cell.children, ['hello world'])

    def test_one_paragraph(self):
        cell = self.get_cell('<p>hello world')
        self.assertEqual(len(cell.children), 1)
        self.assertEqual(cell.children[0].children, ['hello world'])

    def test_two_paragraph(self):
        cell = self.get_cell('<p>hello<p>world')
        self.assertEqual(len(cell.children), 2)
        p1, p2 = cell.children
        self.assertEqual(p1.children, ['hello'])
        self.assertEqual(p2.children, ['world'])

    def test_br_cell(self):
        cell = self.get_cell('<p>hello<br>world')
        self.assertEqual(len(cell.children), 1)
        p = cell.children[0]
        self.assertEqual(len(p.children), 3)
        self.assertEqual(p.children[0], 'hello')
        self.assertEqual(p.children[1].tag, 'br')
        self.assertEqual(p.children[2], 'world')

    def test_recovery(self):
        cell = self.get_cell('<p><p>hello<p><b>world</p>!')
        self.assertEqual(len(cell.children), 4)
        p1, p2, p3, x = cell.children
        self.assertEqual(p1.children, [])
        self.assertEqual(p2.children, ['hello'])
        self.assertEqual(p3.children[0].tag, 'b')
        self.assertEqual(p3.children[0].children, ['world'])
        self.assertEqual(x, '!')


class TestRows(BaseTestCase):

    def get_rows(self, rows):
        return list(self.parse(
            """<table>{}</table>""".format(''.join('<tr><td>'+row+'<td></tr>' for row in rows))
        ))

    def test_two_rows(self):
        rows = self.get_rows(['hello', 'world'])
        self.assertEqual(len(rows), 2)
