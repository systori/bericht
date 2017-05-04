from unittest import TestCase
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter


from bericht import *


rlstyleSheet = getSampleStyleSheet()
rlstyle = rlstyleSheet['BodyText']


def hello(start, end=None, row=None, col=None):
    hellos = ' '.join('hello {}'.format(i) for i in (range(start, end) if end else range(start)))
    return 'Row {} Col {}: {}'.format(row, col, hellos) if row and col else hellos


def hello_p(start, end=None, row=None, col=None):
    return Paragraph(hello(start, end, row, col), rlstyle)


def str_p(paragraph):
    if not paragraph:
        return paragraph
    words = []
    for frag in paragraph.frags:
        words.extend(frag.words if hasattr(frag, 'words') else frag.text.split(' '))
    return ' '.join(words)


class TestCellStyle(TestCase):

    def test_vertical_align(self):
        style = CellStyle()
        self.assertEqual(style.vertical_align, "top")
        style = CellStyle(vertical_align="bottom")
        self.assertEqual(style.vertical_align, "bottom")
        with self.assertRaises(AssertionError):
            style.vertical_align = "foo"


class TestCellWrap(TestCase):

    def test_wrap_single_flowable(self):
        cell = Cell([hello_p(10)])
        self.assertEqual(cell.wrap(50, 10), (50, 126))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 126)
        self.assertEqual(cell._vpos, [0])
        self.assertEqual(cell._heights, [126])

    def test_wrap_multiple_flowables(self):
        cell = Cell([hello_p(10), hello_p(20), hello_p(10)])
        self.assertEqual(cell.wrap(50, 10), (50, 498))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 498)
        self.assertEqual(cell._vpos, [372, 126, 0])
        self.assertEqual(cell._heights, [126, 246, 126])


class TestCellSplit(TestCase):

    def test_no_split(self):
        cell = Cell([hello_p(10)])
        cells = cell.split(50, 126)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0], cell)

    def test_split(self):
        cell = Cell([hello_p(10)])
        cells = cell.split(50, 60)
        self.assertEqual(len(cells), 2)
        top, bottom = [str_p(cell.flowables[0]) for cell in cells]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")


class TestRowStyle(TestCase):

    def test_vertical_align(self):
        style = RowStyle()
        self.assertEqual(style.page_break_inside, True)
        style = RowStyle(page_break_inside=False)
        self.assertEqual(style.page_break_inside, False)
        with self.assertRaises(AssertionError):
            style.page_break_inside = "foo"


class TestRowWrap(TestCase):

    def test_wrap_single_cell_row(self):
        row = Row([Cell([hello_p(10)])])
        self.assertEqual(row.wrap(50, 10), (50, 126))
        self.assertEqual(row.width, 50)
        self.assertEqual(row.height, 126)
        self.assertEqual(row._widths, [50])

    def test_wrap_multi_cell_row(self):
        row = Row([Cell([hello_p(10)]), Cell([hello_p(20)]), Cell([hello_p(10)])])
        self.assertEqual(row.wrap(150, 10), (150, 246))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 246)
        self.assertEqual(row._widths, [50, 50, 50])

    def test_col_span(self):
        row = Row([Cell([hello_p(10)]), Span.COL, Cell([hello_p(10)])])
        self.assertEqual(row.wrap(150, 10), (150, 126))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 126)
        self.assertEqual(row._widths, [100, 50])


class TestRowSplit(TestCase):

    def test_no_split(self):
        row = Row([Cell([hello_p(10)]), Cell([hello_p(10, 20)])])
        rows = row.split(100, 126)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], row)

    def test_split(self):
        row = Row([Cell([hello_p(10)]), Cell([hello_p(10, 20)])])
        rows = row.split(100, 63)
        self.assertEqual(len(rows), 2)
        top1, top2 = [str_p(cell.flowables[0]) for cell in rows[0].cells]
        bottom1, bottom2 = [str_p(cell.flowables[0]) for cell in rows[1].cells]
        self.assertEqual(top1, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom1, "hello 5 hello 6 hello 7 hello 8 hello 9")
        self.assertEqual(top2, "hello 10 hello 11 hello 12 hello 13 hello 14")
        self.assertEqual(bottom2, "hello 15 hello 16 hello 17 hello 18 hello 19")

    def test_split_with_bottom_alignment(self):
        """
            top   |         |  bottom
        -------------------------------
        | hello 0 | hello 0 |         |
        | hello 1 | hello 1 | hello 0 |
        | hello 2 | hello 2 | hello 1 |  <-- split above row
        |         | hello 3 | hello 2 |
        -------------------------------
        """
        row = Row([
            Cell([hello_p(3)]),
            Cell([hello_p(4)]),
            Cell([hello_p(3)], CellStyle(vertical_align="bottom"))
        ])
        rows = row.split(65, 55)
        self.assertEqual(len(rows), 2)
        top1, top2, top3 = [str_p(cell.flowables[0]) for cell in rows[0].cells]
        bottom1, bottom2, bottom3 = [str_p(cell.flowables[0]) for cell in rows[1].cells]
        self.assertEqual(top1, "hello 0 hello 1")
        self.assertEqual(bottom1, "hello 2")
        self.assertEqual(top2, "hello 0 hello 1")
        self.assertEqual(bottom2, "hello 2 hello 3")
        self.assertEqual(top3, "hello 0")
        self.assertEqual(bottom3, "hello 1 hello 2")


class TestTableWrap(TestCase):

    def test_wrap_single_cell(self):
        table = Table([Row([Cell([hello_p(10)])])])
        self.assertEqual(table.wrap(50, 10), (50, 126))
        self.assertEqual(table._heights, [126])

    def test_wrap_uses_tallest_column_in_each_row(self):
        table = Table([
            Row([Cell([hello_p(10)]), Cell([hello_p(20)])]),
            Row([Cell([hello_p(20)]), Cell([hello_p(10)])]),
        ])
        self.assertEqual(table.wrap(100, 10), (100, 492))
        self.assertEqual(table._heights, [246, 246])


class TestTableSplit(TestCase):

    def test_no_split_single_cell(self):
        table = Table([Row([Cell([hello_p(10)])])])
        tables = table.split(50, 126)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0], table)

    def test_split_single_cell(self):
        table = Table([Row([Cell([hello_p(10)])])])
        tables = table.split(50, 60)
        self.assertEqual(len(tables), 2)
        top, bottom = [str_p(table.rows[0].cells[0].flowables[0]) for table in tables]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")

    def test_clean_split_between_rows(self):
        rows = [
            Row([Cell([hello_p(10)])]),
            Row([Cell([hello_p(10)])])
        ]
        table = Table(rows)
        tables = table.split(50, 126)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].rows, [rows[0]])
        self.assertEqual(tables[1].rows, [rows[1]])


class TestTableDraw(TestCase):

    def test_table_draw(self):
        doc = SimpleDocTemplate('mydoc.pdf', pagesize=letter)
        doc.build([Table([
            Row([Cell([hello_p(10, row=i, col=1)]), Cell([hello_p(30, row=i, col=2)])]) for i in range(1, 30)
        ])])


class TestBuilder(TestCase):

    def test_simple_string_cell(self):
        builder = TableBuilder(rlstyle)
        builder.row('hello')
        tbl = builder.table
        self.assertEqual(len(tbl.rows), 1)
        self.assertEqual(len(tbl.rows[0].cells), 1)
        self.assertEqual(len(tbl.rows[0].cells[0].flowables), 1)
        self.assertEqual(str_p(tbl.rows[0].cells[0].flowables[0]), 'hello')

    def test_span(self):
        builder = TableBuilder(rlstyle)
        builder.row('hello', Span.COL, 'world')
        tbl = builder.table
        self.assertEqual(len(tbl.rows), 1)
        self.assertEqual(len(tbl.rows[0].cells), 3)
        self.assertEqual(str_p(tbl.rows[0].cells[0].flowables[0]), 'hello')
        self.assertEqual(tbl.rows[0].cells[1], Span.COL)

    def test_draw_built_table(self):
        builder = TableBuilder(rlstyle)
        builder.row(hello_p(20), Span.COL, hello_p(20))
        builder.row(hello_p(20), hello_p(20), hello_p(20))
        doc = SimpleDocTemplate('builder.pdf', pagesize=letter)
        doc.build([builder.table])
