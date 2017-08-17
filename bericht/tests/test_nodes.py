from bericht.node import *
from bericht.pdf import PDFDocument
from bericht.tests.utils import BaseTestCase


class TestTable(BaseTestCase):

    def test_header_footer(self):
        nodes = self.parse("""
        <table>
          <colgroup>
            <col width="0*">
            <col width="1*">
            <col width="0*">
            <col width="0*">
          </colgroup>
          <thead><tr><td><p>code</td><td><p>name</td><td><p>price</td><td><p>total</td></thead>
          <tfoot><tr><td colspan="4"><p>footer</td></tfoot>
          <tr>
            <td><p>1</td>
            <td><p>First Item</td>
            <td><p>10.00</td>
            <td><p>10.00</td>
          </tr>
          <tr>
            <td><p>2</td>
            <td><p>{}</td>
            <td><p>15.00</td>
            <td><p>25.00</td>
          </tr>
        </table>
        """.format('Second Long Item '*1000))

        row1, row2 = nodes
        self.assertIsInstance(row1, Row)
        self.assertIsInstance(row2, Row)

        page = PDFDocument(nodes.css).add_page()

        row1.wrap(page, page.available_width)
        row1.draw(page, page.x, page.y)
