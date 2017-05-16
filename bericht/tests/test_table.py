from unittest import TestCase
from bericht.style import *
from bericht.table import *
from bericht.text import *


S = Style.default()

hello_width = Word(S, 'hello 99').width
hello_height = S.leading


def hello(start, end=None, row=None, col=None):
    hellos = ' '.join('hello {}'.format(i) for i in (range(start, end) if end else range(start)))
    return 'Row {} Col {}: {}'.format(row, col, hellos) if row and col else hellos


def hello_p(start, end=None, row=None, col=None):
    return Paragraph.from_string(hello(start, end, row, col), S)


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
        cell = Cell([hello_p(10)], S)
        self.assertEqual(cell.wrap(50), (50, 140))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 140)
        self.assertEqual(cell._vpos, [0])
        self.assertEqual(cell._heights, [140])

    def test_wrap_multiple_flowables(self):
        cell = Cell([hello_p(10), hello_p(20), hello_p(10)], S)
        self.assertEqual(cell.wrap(50), (50, 560))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 560)
        self.assertEqual(cell._vpos, [420, 140, 0])
        self.assertEqual(cell._heights, [140, 280, 140])


class TestCellSplit(TestCase):

    def test_no_split(self):
        cell = Cell([hello_p(10)], S)
        cells = cell.split(50, 140)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0], cell)

    def test_split(self):
        cell = Cell([hello_p(10)], S)
        cells = cell.split(50, 70)
        self.assertEqual(len(cells), 2)
        top, bottom = [str(cell.flowables[0]) for cell in cells]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")


class TestRowWrap(TestCase):

    def test_wrap_single_cell_row(self):
        row = Row([Cell([hello_p(10)], S)], S)
        self.assertEqual(row.wrap([50]), (50, 140))
        self.assertEqual(row.width, 50)
        self.assertEqual(row.height, 140)
        self.assertEqual(row.cell_widths, [50])
        self.assertEqual(row.column_widths, [50])

    def test_wrap_multi_cell_row(self):
        row = Row([
            Cell([hello_p(10)], S),
            Cell([hello_p(20)], S),
            Cell([hello_p(10)], S)
        ], S)
        self.assertEqual(row.wrap([50, 50, 50]), (150, 280))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 280)
        self.assertEqual(row.cell_widths, [50, 50, 50])
        self.assertEqual(row.column_widths, [50, 50, 50])

    def test_col_span(self):
        row = Row([
            Cell([hello_p(10)], S),
            Span.col,
            Cell([hello_p(10)], S)
        ], S)
        self.assertEqual(row.wrap([50, 50, 50]), (150, 140))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 140)
        self.assertEqual(row.cell_widths, [100, 50])
        self.assertEqual(row.column_widths, [50, 50, 50])


class TestRowSplit(TestCase):

    def test_no_split(self):
        row = Row([
            Cell([hello_p(10)], S),
            Cell([hello_p(10, 20)], S)
        ], S)
        rows = row.split([50, 50], 140)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], row)

    def test_split(self):
        row = Row([
            Cell([hello_p(10)], S),
            Cell([hello_p(10, 20)], S)
        ], S)
        width, height = [hello_width * 5, hello_width * 6], hello_height
        rows = row.split(width, height)
        self.assertEqual(len(rows), 2)
        top1, top2 = row_lines(rows[0], width, height)
        bottom1, bottom2 = row_lines(rows[1], width, height)
        self.assertEqual(top1, ["hello 0 hello 1 hello 2 hello 3 hello 4"])
        self.assertEqual(bottom1, ["hello 5 hello 6 hello 7 hello 8 hello 9"])
        self.assertEqual(top2, ["hello 10 hello 11 hello 12 hello 13 hello 14"])
        self.assertEqual(bottom2, ["hello 15 hello 16 hello 17 hello 18 hello 19"])

    def test_split_w_span(self):
        row = Row([
            Cell([hello_p(10)], S),
            Span.col,
            Cell([hello_p(10, 20)], S)
        ], S)
        width, height = [hello_width * 3, hello_width * 2, hello_width * 6], hello_height
        rows = row.split(width, height)
        self.assertEqual(len(rows), 2)
        top1, top2 = row_lines(rows[0], width, height)
        bottom1, bottom2 = row_lines(rows[1], width, height)
        self.assertEqual(top1, ["hello 0 hello 1 hello 2 hello 3 hello 4"])
        self.assertEqual(bottom1, ["hello 5 hello 6 hello 7 hello 8 hello 9"])
        self.assertEqual(top2, ["hello 10 hello 11 hello 12 hello 13 hello 14"])
        self.assertEqual(bottom2, ["hello 15 hello 16 hello 17 hello 18 hello 19"])

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
            Cell([hello_p(3)], S),
            Cell([hello_p(4)], S),
            Cell([hello_p(3)], S.set(vertical_align=VerticalAlign.bottom))
        ], S)
        width, height = [hello_width+1]*3, 2 * hello_height + 1
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
        table = Table([0], [Row([Cell([hello_p(10)], S)], S)], S)
        self.assertEqual(table.wrap(50, 10), (50, 140))
        self.assertEqual(table._heights, [140])

    def test_wrap_uses_tallest_column_in_each_row(self):
        table = Table([0, 0], [
            Row([Cell([hello_p(10)], S), Cell([hello_p(20)], S)], S),
            Row([Cell([hello_p(20)], S), Cell([hello_p(10)], S)], S),
        ], S)
        self.assertEqual(table.wrap(100, 10), (100, 560))
        self.assertEqual(table._heights, [280, 280])


class TestTableSplit(TestCase):

    def test_no_split_single_cell(self):
        table = Table([0], [Row([Cell([hello_p(10)], S)], S)], S)
        tables = table.split(50, 140)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0], table)

    def test_split_single_cell(self):
        table = Table([0], [Row([Cell([hello_p(10)], S)], S)], S)
        width, height = 5 * hello_width, hello_height
        tables = table.split(width, height)
        self.assertEqual(len(tables), 2)
        top, bottom = [row_lines(table.rows[0], [width], height)[0] for table in tables]
        self.assertEqual(top, ["hello 0 hello 1 hello 2 hello 3 hello 4"])
        self.assertEqual(bottom, ["hello 5 hello 6 hello 7 hello 8 hello 9"])

    def test_clean_split_between_rows(self):
        rows = [
            Row([Cell([hello_p(10)], S)], S),
            Row([Cell([hello_p(10)], S)], S)
        ]
        table = Table([0], rows, S)
        tables = table.split(50, 140)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].rows, [rows[0]])
        self.assertEqual(tables[1].rows, [rows[1]])


class TestBuilder(TestCase):

    def test_simple_string_cell(self):
        builder = TableBuilder([0], S)
        builder.row('hello')
        tbl = builder.table
        tbl.wrap(100)
        self.assertEqual(len(tbl.rows), 1)
        self.assertEqual(len(tbl.rows[0].cells), 1)
        self.assertEqual(len(tbl.rows[0].cells[0].flowables), 1)
        self.assertEqual(row_lines(tbl.rows[0], [100], 100), [['hello']])

    def test_span(self):
        builder = TableBuilder([0, 1, 1], S)
        builder.row('hello', Span.col, 'world')
        tbl = builder.table
        tbl.wrap(150)
        self.assertEqual(len(tbl.rows), 1)
        row = tbl.rows[0]
        self.assertEqual(len(row.columns), 3)
        self.assertEqual(len(row.cells), 2)
        self.assertEqual(row_lines(row, [50, 50, 50], 100), [['hello'], ['world']])
