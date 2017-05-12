from unittest import TestCase
from bericht.style import *
from bericht.table import *
from bericht.text import *


block_style = BlockStyle.default()
table_style = TableStyle.from_style(block_style)
row_style = RowStyle.from_style(block_style)
cell_style = CellStyle.from_style(block_style)
text_style = TextStyle.from_style(block_style)

hello_width = Word(text_style, 'hello 99').width
hello_height = text_style.leading


def hello(start, end=None, row=None, col=None):
    hellos = ' '.join('hello {}'.format(i) for i in (range(start, end) if end else range(start)))
    return 'Row {} Col {}: {}'.format(row, col, hellos) if row and col else hellos


def hello_p(start, end=None, row=None, col=None):
    return Paragraph.from_string(hello(start, end, row, col), block_style)


def row_lines(row, width, height):
    row.wrap(width, height)
    cells = []
    for cell in row.cells:
        if isinstance(cell, Span):
            cells.append(cell)
            continue
        lines = []
        for p in cell.flowables:
            for line in p.lines:
                lines.append(' '.join(str(w) for w in line))
        cells.append(lines)
    return cells


class TestCellWrap(TestCase):

    def test_wrap_single_flowable(self):
        cell = Cell([hello_p(10)], cell_style)
        self.assertEqual(cell.wrap(50, 10), (50, 140))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 140)
        self.assertEqual(cell._vpos, [0])
        self.assertEqual(cell._heights, [140])

    def test_wrap_multiple_flowables(self):
        cell = Cell([hello_p(10), hello_p(20), hello_p(10)], cell_style)
        self.assertEqual(cell.wrap(50, 10), (50, 560))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 560)
        self.assertEqual(cell._vpos, [420, 140, 0])
        self.assertEqual(cell._heights, [140, 280, 140])


class TestCellSplit(TestCase):

    def test_no_split(self):
        cell = Cell([hello_p(10)], cell_style)
        cells = cell.split(50, 140)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0], cell)

    def test_split(self):
        cell = Cell([hello_p(10)], cell_style)
        cells = cell.split(50, 70)
        self.assertEqual(len(cells), 2)
        top, bottom = [str(cell.flowables[0]) for cell in cells]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")


class TestRowWrap(TestCase):

    def test_wrap_single_cell_row(self):
        row = Row([Cell([hello_p(10)], cell_style)], row_style)
        self.assertEqual(row.wrap(50, 10), (50, 140))
        self.assertEqual(row.width, 50)
        self.assertEqual(row.height, 140)
        self.assertEqual(row._widths, [50])

    def test_wrap_multi_cell_row(self):
        row = Row([
            Cell([hello_p(10)], cell_style),
            Cell([hello_p(20)], cell_style),
            Cell([hello_p(10)], cell_style)
        ], row_style)
        self.assertEqual(row.wrap(150, 10), (150, 280))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 280)
        self.assertEqual(row._widths, [50, 50, 50])

    def test_col_span(self):
        row = Row([
            Cell([hello_p(10)], cell_style),
            Span.col,
            Cell([hello_p(10)], cell_style)
        ], row_style)
        self.assertEqual(row.wrap(150, 10), (150, 140))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 140)
        self.assertEqual(row._widths, [100, 50])


class TestRowSplit(TestCase):

    def test_no_split(self):
        row = Row([
            Cell([hello_p(10)], cell_style),
            Cell([hello_p(10, 20)], cell_style)
        ], row_style)
        rows = row.split(100, 140)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], row)

    def test_split(self):
        row = Row([
            Cell([hello_p(10)], cell_style),
            Cell([hello_p(10, 20)], cell_style)
        ], row_style)
        rows = row.split(100, 70)
        self.assertEqual(len(rows), 2)
        top1, top2 = [str(cell.flowables[0]) for cell in rows[0].cells]
        bottom1, bottom2 = [str(cell.flowables[0]) for cell in rows[1].cells]
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
            Cell([hello_p(3)], cell_style),
            Cell([hello_p(4)], cell_style),
            Cell([hello_p(3)], cell_style.set(vertical_align=VerticalAlign.bottom))
        ], row_style)
        width, height = 3 * hello_width + 1, 2 * hello_height + 1
        rows = row.split(width, height)
        self.assertEqual(len(rows), 2)
        top1, top2, top3 = row_lines(rows[0], width, height)
        self.assertEqual(top1, ["hello 0", "hello 1"])
        self.assertEqual(top2, ["hello 0", "hello 1"])
        self.assertEqual(top3, ["hello 0"])
        bottom1, bottom2, bottom3 = row_lines(rows[1], width, height)
        self.assertEqual(bottom1, ["hello 2"])
        self.assertEqual(bottom2, ["hello 2", "hello 3"])
        self.assertEqual(bottom3, ["hello 1", "hello 2"])


class TestTableWrap(TestCase):

    def test_wrap_single_cell(self):
        table = Table([Row([Cell([hello_p(10)], cell_style)], row_style)], table_style)
        self.assertEqual(table.wrap(50, 10), (50, 140))
        self.assertEqual(table._heights, [140])

    def test_wrap_uses_tallest_column_in_each_row(self):
        table = Table([
            Row([Cell([hello_p(10)], cell_style), Cell([hello_p(20)], cell_style)], row_style),
            Row([Cell([hello_p(20)], cell_style), Cell([hello_p(10)], cell_style)], row_style),
        ], table_style)
        self.assertEqual(table.wrap(100, 10), (100, 560))
        self.assertEqual(table._heights, [280, 280])


class TestTableSplit(TestCase):

    def test_no_split_single_cell(self):
        table = Table([Row([Cell([hello_p(10)], cell_style)], row_style)], table_style)
        tables = table.split(50, 140)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0], table)

    def test_split_single_cell(self):
        table = Table([Row([Cell([hello_p(10)], cell_style)], row_style)], table_style)
        width, height = 5 * hello_width, hello_height
        tables = table.split(width, height)
        self.assertEqual(len(tables), 2)
        top, bottom = [row_lines(table.rows[0], width, height)[0] for table in tables]
        self.assertEqual(top, ["hello 0 hello 1 hello 2 hello 3 hello 4"])
        self.assertEqual(bottom, ["hello 5 hello 6 hello 7 hello 8 hello 9"])

    def test_clean_split_between_rows(self):
        rows = [
            Row([Cell([hello_p(10)], cell_style)], row_style),
            Row([Cell([hello_p(10)], cell_style)], row_style)
        ]
        table = Table(rows, table_style)
        tables = table.split(50, 140)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].rows, [rows[0]])
        self.assertEqual(tables[1].rows, [rows[1]])


class TestBuilder(TestCase):

    def test_simple_string_cell(self):
        builder = TableBuilder(table_style)
        builder.row('hello')
        tbl = builder.table
        self.assertEqual(len(tbl.rows), 1)
        self.assertEqual(len(tbl.rows[0].cells), 1)
        self.assertEqual(len(tbl.rows[0].cells[0].flowables), 1)
        self.assertEqual(row_lines(tbl.rows[0], 100, 100), [['hello']])

    def test_span(self):
        builder = TableBuilder(table_style)
        builder.row('hello', Span.col, 'world')
        tbl = builder.table
        self.assertEqual(len(tbl.rows), 1)
        self.assertEqual(len(tbl.rows[0].cells), 3)
        self.assertEqual(row_lines(tbl.rows[0], 100, 100), [['hello'], Span.col, ['world']])

    def test_draw_built_table(self):
        builder = TableBuilder(table_style)
        builder.row(hello_p(20), Span.col, hello_p(20))
        builder.row(hello_p(20), hello_p(20), hello_p(20))
