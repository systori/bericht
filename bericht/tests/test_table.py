from unittest import TestCase
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Flowable
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate, LayoutError
from reportlab.lib.pagesizes import letter


styleSheet = getSampleStyleSheet()
style = styleSheet['BodyText']


class Table(Flowable):

    def __init__(self, rows):
        super().__init__()
        assert rows, "Cannot create a table with no rows."
        self.rows = rows
        self.columns_count = 0
        for row in self.rows:
            self.columns_count = max(len(row), self.columns_count)
        self._row_heights = None
        self._row_offsets = None
        self._col_widths = None
        self._col_offsets = None

    def draw(self):
        for row, height, y in zip(self.rows, self._row_heights, self._row_offsets):
            for cell, width, x in zip(row, self._col_widths, self._col_offsets):
                self.draw_cell(cell, (x, y), (width, height))

    def draw_cell(self, cell, position, size):
        if not cell:
            return
        x, y = position
        width, height = size
        cell.drawOn(self.canv, x, y)
        self.canv.rect(x, y, width, height)

    def wrap(self, available_width, available_height):
        """ Constrains each row to the available_width and records
            the height of the tallest cell in each row. Returns
            a tuple of (available_width, sum of all row heights).

            Also, calculates the row and column positions for draw
            operation.
        """
        col_width = float(available_width) / self.columns_count
        consumed_height = 0

        self._col_widths = [col_width] * self.columns_count
        self._row_heights = []
        for row in self.rows:
            row_height = 0
            for col_idx, col in enumerate(row):
                if col:
                    width, height = col.wrapOn(None, self._col_widths[col_idx], available_height - consumed_height)
                    row_height = max(height, row_height)
            self._row_heights.append(row_height)
            consumed_height += row_height

        # columns are positioned left -> right
        self._col_offsets = [sum(self._col_widths[:i]) for i in range(len(self._col_widths))]
        # rows are positioned bottom -> top
        self._row_offsets = [sum(self._row_heights[i:]) for i in range(len(self._row_heights))]

        return available_width, consumed_height

    def split(self, available_width, available_height):
        """ Split this table into two where the first table
            is within the constraints of available_width and
            available_height and the second table is everything
            that's left over.
        """
        if self._row_heights is None:
            self.wrap(available_width, available_height)

        assert self._row_heights, "Split called on empty table."

        split_at_row = -1
        split_row_height = 0
        consumed_height = 0
        for height in self._row_heights:
            split_at_row += 1
            split_row_height = height
            consumed_height += height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.rows) == 1 or len(self.rows)-1 == split_at_row:
                # nothing to split
                return []
            else:
                # table split cleanly after a row, no need to further split any rows/cells
                return [
                    Table(self.rows[:split_at_row+1]),
                    Table(self.rows[split_at_row-1:])
                ]

        top_rows = self.rows[:split_at_row]
        split_row = self.rows[split_at_row]
        bottom_rows = self.rows[split_at_row+1:]

        top_half = []
        bottom_half = []
        top_height = available_height - (consumed_height - split_row_height)
        for col_idx, cell in enumerate(split_row):
            split = cell.split(self._col_widths[col_idx], top_height)
            if not split:
                # cell could not be split,
                # move entirely to bottom half
                top_half.append(None)
                bottom_half.append(cell)
            elif len(split) == 1:
                # cell completely fits in top half,
                # add placeholder to bottom half
                top_half.append(cell)
                bottom_half.append(None)
            elif len(split) == 2:
                top_half.append(split[0])
                bottom_half.append(split[1])
            else:
                raise LayoutError("Splitting cell {} produced unexpected result.".format(cell))

        if any(top_half):
            top_rows.append(top_half)

        if any(bottom_half):
            bottom_rows.insert(0, bottom_half)

        return [
            Table(top_rows),
            Table(bottom_rows)
        ]


def hello_p(repeated, row=None, col=None):
    if row and col:
        return Paragraph(
            'Row {} Col {}: {}'.format(
                row, col, ' '.join('hello {}'.format(i) for i in range(repeated))
            ), style
        )
    else:
        return Paragraph(' '.join('hello {}'.format(i) for i in range(repeated)), style)


def str_p(paragraph):
    words = []
    for frag in paragraph.frags:
        words.extend(frag.words)
    return ' '.join(words)


class TestWrapTable(TestCase):

    def test_wrap_single_cell(self):
        table = Table([[hello_p(10)]])
        self.assertEqual(table.wrap(50, 10), (50, 120))
        self.assertEqual(table._col_widths, [50])
        self.assertEqual(table._col_offsets, [0])
        self.assertEqual(table._row_heights, [120])
        self.assertEqual(table._row_offsets, [120])

    def test_wrap_uses_tallest_column_in_each_row(self):
        table = Table([
            [hello_p(10), hello_p(20)],
            [hello_p(20), hello_p(10)],
        ])
        self.assertEqual(table.wrap(100, 10), (100, 480))
        self.assertEqual(table._col_widths, [50, 50])
        self.assertEqual(table._col_offsets, [0, 50])
        self.assertEqual(table._row_heights, [240, 240])
        self.assertEqual(table._row_offsets, [480, 240])


class TestSplitTable(TestCase):

    def test_no_split_single_cell(self):
        table = Table([[hello_p(10)]])
        tables = table.split(50, 120)
        self.assertEqual(len(tables), 0)

    def test_split_single_cell(self):
        table = Table([[hello_p(10)]])
        tables = table.split(50, 60)
        self.assertEqual(len(tables), 2)
        top, bottom = [str_p(tbl.rows[0][0]) for tbl in tables]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")


class TestTableDraw(TestCase):

    def test_table_draw(self):
        doc = SimpleDocTemplate('mydoc.pdf', pagesize=letter)
        doc.build([Table([
            [hello_p(10, i, 1), hello_p(20, i, 2)] for i in range(1, 10)
        ])])
