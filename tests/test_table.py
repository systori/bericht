from unittest import TestCase
from reportlab.pdfgen.canvas import Canvas

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
    return para(hello(start, end, row, col))


def row_lines(row, width, height):
    row.wrap(width, height)
    cells = []
    for cell in row.content:
        if isinstance(cell, Span):
            cells.append(cell)
            continue
        lines = []
        for p in cell.content:
            if isinstance(p, Paragraph):
                for line in p.content:
                    lines.append(' '.join(str(w) for w in line))
            elif isinstance(p, Text):
                lines.append(p.text)
            else:
                raise ValueError
        cells.append(lines)
    return cells


class RecordingParagraph(Paragraph):

    def __init__(self, words, style):
        super().__init__(words, style)
        self.draw_call = None

    def drawOn(self, canvas, x, y, _sW=None):
        self.draw_call = (x, y)
        super().drawOn(canvas, x, y, _sW)


def rpara(text, style):
    return RecordingParagraph.from_string(text, style)


class TestCell(TestCase):

    def setUp(self):
        self.text = 'hello'
        self.p = rpara(self.text, S)
        self.width = self.p.width
        self.height = S.leading

    def test_frame(self):
        frame = S.set(
            margin_top=1,
            margin_right=2,
            margin_bottom=3,
            margin_left=4,
            border_top_width=5,
            border_right_width=6,
            border_bottom_width=7,
            border_left_width=8,
            padding_top=9,
            padding_right=10,
            padding_bottom=11,
            padding_left=12,
        )
        cell = Cell([], frame)
        cell.collapsed = False
        self.assertEqual(cell.frame_top, 14)
        self.assertEqual(cell.frame_right, 16)
        self.assertEqual(cell.frame_bottom, 18)
        self.assertEqual(cell.frame_left, 20)
        self.assertEqual(cell.frame_width, 36)
        self.assertEqual(cell.frame_height, 32)
        cell.collapsed = True
        self.assertEqual(cell.frame_top, 11.5)
        self.assertEqual(cell.frame_right, 13)
        self.assertEqual(cell.frame_bottom, 14.5)
        self.assertEqual(cell.frame_left, 16)
        self.assertEqual(cell.frame_width, 29)
        self.assertEqual(cell.frame_height, 26)

    def test_wrap(self):
        cell = Cell([self.p], S.set(padding_top=3, padding_bottom=3))
        self.assertEqual(cell.wrap(50), (50, self.height + 6))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, self.height + 6)
        self.assertEqual(cell.content_heights, [self.height])

    def test_wrap_multiple_flowables(self):
        cell = Cell(
            [hello_p(10), hello_p(20), hello_p(10)],
            S.set(padding_top=3, padding_bottom=3))
        self.assertEqual(cell.wrap(50), (50, 560 + 6))
        self.assertEqual(cell.width, 50)
        self.assertEqual(cell.height, 560 + 6)
        self.assertEqual(cell.content_heights, [140, 280, 140])

    def test_no_split(self):
        cell = Cell([hello_p(10)], S)
        cells = cell.split(50, 140)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0], cell)
        self.assertEqual(cells[0].was_split, False)

    def test_split(self):
        cell = Cell([hello_p(10)], S)
        cells = cell.split(50, 70)
        self.assertEqual(len(cells), 2)
        self.assertEqual(cells[0].was_split, True)
        self.assertEqual(cells[1].was_split, True)
        top, bottom = [str(cell.content[0]) for cell in cells]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")

    def test_draw(self):
        canvas = Canvas(None)
        p1 = rpara(self.text, S)
        p2 = rpara(self.text, S)
        cell = Cell([p1, p2], S.set(padding_left=1, padding_top=3, padding_bottom=3))
        # natural height, aligned top
        cell.wrap(30)
        cell.drawOn(canvas, 0, 0)
        self.assertEqual(p1.draw_call, (1, 17))
        self.assertEqual(p2.draw_call, (1, 3))
        # force different height
        cell.height = 100
        cell.drawOn(canvas, 0, 0)
        self.assertEqual(p1.draw_call, (1, 83))
        self.assertEqual(p2.draw_call, (1, 69))
        # height 100 and aligned to bottom
        cell.style = cell.style.set(vertical_align=VerticalAlign.bottom)
        cell.drawOn(canvas, 0, 0)
        self.assertEqual(p1.draw_call, (1, 17))
        self.assertEqual(p2.draw_call, (1, 3))
        # middle aligned
        cell.style = cell.style.set(vertical_align=VerticalAlign.middle)
        cell.drawOn(canvas, 0, 0)
        self.assertEqual(p1.draw_call, (1, 50))
        self.assertEqual(p2.draw_call, (1, 36))


class TestRow(TestCase):

    def test_frame(self):
        # rows only care about border_top and
        # border_bottom when in collapsed mode,
        # everything else is ignored
        frame = S.set(
            margin_top=1,
            margin_right=2,
            margin_bottom=3,
            margin_left=4,
            border_top_width=5,
            border_right_width=6,
            border_bottom_width=7,
            border_left_width=8,
            padding_top=9,
            padding_right=10,
            padding_bottom=11,
            padding_left=12,
        )
        row = Row([], frame)
        row.collapsed = False
        self.assertEqual(row.frame_top, 0)
        self.assertEqual(row.frame_right, 0)
        self.assertEqual(row.frame_bottom, 0)
        self.assertEqual(row.frame_left, 0)
        self.assertEqual(row.frame_width, 0)
        self.assertEqual(row.frame_height, 0)
        row.collapsed = True
        self.assertEqual(row.frame_top, 5)
        self.assertEqual(row.frame_right, 0)
        self.assertEqual(row.frame_bottom, 7)
        self.assertEqual(row.frame_left, 0)
        self.assertEqual(row.frame_width, 0)
        self.assertEqual(row.frame_height, 12)

    def test_wrap(self):
        row = Row(
            [Cell([hello_p(10)], S)],
            S.set(border_top_width=3, border_bottom_width=3)
        )
        row.collapsed = True
        self.assertEqual(row.wrap([50]), (50, 140 + 6))
        self.assertEqual(row.width, 50)
        self.assertEqual(row.height, 140 + 6)
        self.assertEqual(row.content_widths, [50])
        self.assertEqual(row.column_widths, [50])

    def test_wrap_equalized_height(self):
        row = Row([
            Cell([hello_p(10)], S),
            Cell([hello_p(20)], S),
            Cell([hello_p(10)], S)
        ], S)
        self.assertEqual(row.wrap([50, 50, 50]), (150, 280))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 280)
        # override individual cell heights to match the tallest cell
        self.assertEqual(row.content[0].height, 280)
        self.assertEqual(row.content[1].height, 280)
        self.assertEqual(row.content[2].height, 280)
        self.assertEqual(row.content_widths, [50, 50, 50])
        self.assertEqual(row.column_widths, [50, 50, 50])

    def test_wrap_with_span(self):
        row = Row([
            Cell([hello_p(10)], S),
            Span.col,
            Cell([hello_p(10)], S)
        ], S)
        self.assertEqual(row.wrap([50, 50, 50]), (150, 140))
        self.assertEqual(row.width, 150)
        self.assertEqual(row.height, 140)
        self.assertEqual(row.content[0].height, 140)
        self.assertEqual(row.content[1].height, 140)
        self.assertEqual(row.content_widths, [100, 50])
        self.assertEqual(row.column_widths, [50, 50, 50])

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
        self.assertEqual(rows[0].was_split, True)
        self.assertEqual(rows[1].was_split, True)
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

    def test_split_w_span_should_fail_for_lack_of_vertical_space(self):
        """
        Ask row to split but don't give enough height to fit a single
        line of text.
        Tests a regression where an empty row was considered not-empty
        because Span.col evaluated to not None.
        """
        row = Row([Cell([hello_p(10)], S), Span.col], S)
        rows = row.split([hello_width * 3, hello_width * 2], hello_height * .9)
        self.assertEqual(len(rows), 0)

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


class TestTable(TestCase):

    def test_wrap_single_cell(self):
        table = Table([1], [0], [Row([Cell([hello_p(10)], S)], S)], S)
        self.assertEqual(table.wrap(50, 10), (50, 142))
        self.assertEqual(table.content_heights, [142])

    def test_wrap_uses_tallest_column_in_each_row(self):
        table = Table([1, 1], [0, 0], [
            Row([Cell([hello_p(10)], S), Cell([hello_p(20)], S)], S),
            Row([Cell([hello_p(20)], S), Cell([hello_p(10)], S)], S),
        ], S)
        self.assertEqual(table.wrap(100, 10), (100, 564))
        self.assertEqual(table.content_heights, [282, 282])

    def test_no_split_single_cell(self):
        table = Table([1], [0], [Row([Cell([hello_p(10)], S)], S)], S)
        tables = table.split(50, 142)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0], table)

    def test_split_single_cell(self):
        table = Table([1], [0], [Row([Cell([hello_p(10)], S)], S)], S)
        width, height = 5 * hello_width, hello_height + 2
        tables = table.split(width, height)
        self.assertEqual(len(tables), 2)
        top, bottom = [row_lines(table.content[0], [width], height)[0] for table in tables]
        self.assertEqual(top, ["hello 0 hello 1 hello 2 hello 3 hello 4"])
        self.assertEqual(bottom, ["hello 5 hello 6 hello 7 hello 8 hello 9"])

    def test_clean_split_between_rows(self):
        rows = [
            Row([Cell([hello_p(10)], S)], S),
            Row([Cell([hello_p(10)], S)], S)
        ]
        table = Table([1], [0], rows, S)
        tables = table.split(50, 142)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].content, [rows[0]])
        self.assertEqual(tables[1].content, [rows[1]])

    def test_calculate_ratios(self):
        table = Table([0, 1, 0], [25, 0, 100], [], S)
        self.assertEqual(table.content_widths, None)
        table.calculate_ratio_columns(200)
        self.assertEqual(table.content_widths, [25, 75, 100])

    def test_header_footer_split(self):
        thead = [  # height: 16
            Row([Cell([static('heading', S)], S)], S)
        ]
        tbody = [  # height: 142
            Row([Cell([hello_p(10)], S)], S),
            Row([Cell([hello_p(10)], S)], S)
        ]
        tfoot = [  # height: 16
            Row([Cell([static('footer', S)], S)], S)
        ]
        table = Table([1], [0], tbody, S, thead, tfoot)
        tables = table.split(50, 16 + 142 + 16)
        self.assertEqual(len(tables), 2)
        self.assertEqual(list(tables[0].rows), [thead[0], tbody[0], tfoot[0]])
        self.assertEqual(list(tables[1].rows), [thead[0], tbody[1], tfoot[0]])


class TestBuilder(TestCase):

    def test_basic(self):
        builder = TableBuilder([1, 0, 0], S)
        builder.row(para('hello'), 'world', 99)
        tbl = builder.table
        tbl.wrap(100)
        rows = tbl.content
        self.assertEqual(len(rows), 1)
        cells = rows[0].content
        self.assertEqual(len(cells), 3)
        self.assertIsInstance(cells[0].content[0], Paragraph)
        self.assertIsInstance(cells[1].content[0], Text)
        self.assertIsInstance(cells[2].content[0], Text)
        self.assertEqual(row_lines(tbl.content[0], tbl.content_widths, 100), [
            ['hello'], ['world'], ['99']
        ])

    def test_span(self):
        builder = TableBuilder([1, 1, 1], S)
        builder.row('hello', Span.col, 'world')
        tbl = builder.table
        tbl.wrap(150)
        rows = tbl.content
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(len(row.columns), 3)
        self.assertEqual(len(row.content), 2)
        self.assertEqual(row.content_widths, [97, 48])
        self.assertEqual(row_lines(row, tbl.content_widths, 100), [
            ['hello'], ['world']
        ])

    def test_bigger_table_with_spanning(self):
        builder = TableBuilder([0, 1, 0, 0], S)
        builder.row('col 1', 'col 2', 'col 3', 'col 4')
        builder.row('row 1', hello_p(10), Span.col, 99)
        builder.row('row 1.1', 'stuff', 'more stuff', 11)
        tbl = builder.table

        tbl.wrap(500)
        rows = tbl.content
        self.assertEqual(len(rows), 3)
        row1, row2, row3 = rows
        self.assertEqual(len(row1.content), 4)
        self.assertEqual(len(row2.content), 3)
        self.assertEqual(len(row3.content), 4)
        self.assertEqual(row_lines(row1, tbl.content_widths, 1000), [
            ['col 1'], ['col 2'], ['col 3'], ['col 4']
        ])
        self.assertEqual(row_lines(row2, tbl.content_widths, 1000), [
            ['row 1'], [hello(10)], ['99']
        ])
        self.assertEqual(row_lines(row3, tbl.content_widths, 1000), [
            ['row 1.1'], ['stuff'], ['more stuff'], ['11']
        ])

        # with table split
        tbl.wrap(305)
        tbl1, tbl2 = tbl.split(305, 40)
        tbl1.wrap(305)
        row1, row2 = tbl1.content
        self.assertEqual(len(row1.content), 4)
        self.assertEqual(len(row2.content), 3)
        self.assertEqual(row_lines(row1, tbl.content_widths, 1000), [
            ['col 1'], ['col 2'], ['col 3'], ['col 4']
        ])
        self.assertEqual(row_lines(row2, tbl.content_widths, 1000), [
            ['row 1'], [hello(6)], ['99']
        ])
        tbl2.wrap(300)
        row1, row2 = tbl2.content
        self.assertEqual(len(row1.content), 3)
        self.assertEqual(len(row2.content), 4)
        self.assertEqual(row_lines(row1, tbl.content_widths, 1000), [
            [], [hello(6, 10)], []
        ])
        self.assertEqual(row_lines(row2, tbl.content_widths, 1000), [
            ['row 1.1'], ['stuff'], ['more stuff'], ['11']
        ])
