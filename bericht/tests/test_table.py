from unittest import TestCase
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Flowable
from reportlab.platypus.paragraph import Paragraph as P

styleSheet = getSampleStyleSheet()
style = styleSheet['BodyText']


class Table(Flowable):

    def __init__(self, rows):
        super().__init__()
        self.rows = rows
        self.columns_count = 0
        for row in self.rows:
            self.columns_count = max(len(row), self.columns_count)
        self._row_heights = None
        self._col_widths = None

    def draw(self):
        for row in self.rows:
            for cell in row:
                self.draw_cell(cell)

    def draw_cell(self, cell):
        return

    def wrap(self, available_width, available_height):
        """
        Constrains each row to the available_width and records
        the height of the tallest cell in each row. Returns
        a tuple of available_width and a sum of all row heights.
        :param available_width: 
        :param available_height: 
        :return: consumed_width, consumed_height
        """
        col_width = float(available_width) / self.columns_count
        consumed_height = 0
        self._col_widths = [col_width] * self.columns_count  # TODO: calculate this from actual cells
        self._row_heights = []
        for row in self.rows:
            row_height = 0
            for col_idx, col in enumerate(row):
                width, height = col.wrapOn(None, self._col_widths[col_idx], available_height - consumed_height)
                row_height = max(height, row_height)
            self._row_heights.append(row_height)
            consumed_height += row_height
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
        consumed_height = 0
        for height in self._row_heights:
            split_at_row += 1
            consumed_height += height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.rows) <= 1 or len(self.rows)-1 == split_at_row:
                return []  # nothing to split
            return [
                Table(self.rows[:split_at_row+1]),
                Table(self.rows[split_at_row-1:])
            ]

        top_rows = self.rows[:split_at_row]
        split_row = self.rows[split_at_row]
        bottom_rows = self.rows[split_at_row+1:]

        top_half = []
        bottom_half = []
        for col_idx, cell in enumerate(split_row):
            split = cell.split(self._col_widths[col_idx], available_height)
            if split:
                top_half.append(split[0])
                bottom_half.append(split[1])
            else:
                top_half.append(cell)
                bottom_half.append('')

        top_rows.append(top_half)
        bottom_rows.insert(0, bottom_half)

        return [
            Table(top_rows),
            Table(bottom_rows)
        ]


def hello_p(repeated):
    return P(' '.join('hello {}'.format(i) for i in range(repeated)), style)


def str_p(paragraph):
    words = []
    for frag in paragraph.frags:
        words.extend(frag.words)
    return ' '.join(words)


class TestWrapTable(TestCase):

    def test_wrap_single_cell(self):
        self.table = Table([[hello_p(10)]])
        self.assertEqual(self.table.wrap(50, 10), (50, 120))
        self.assertEqual(self.table._col_widths, [50])
        self.assertEqual(self.table._row_heights, [120])

    def test_wrap_uses_tallest_column_in_each_row(self):
        self.table = Table([
            [hello_p(10), hello_p(20)],
            [hello_p(20), hello_p(10)],
        ])
        self.assertEqual(self.table.wrap(100, 10), (100, 480))
        self.assertEqual(self.table._col_widths, [50, 50])
        self.assertEqual(self.table._row_heights, [240, 240])


class TestSplitTable(TestCase):

    def test_no_split_single_cell(self):
        self.table = Table([[hello_p(10)]])
        tables = self.table.split(50, 120)
        self.assertEqual(len(tables), 0)

    def test_split_single_cell(self):
        self.table = Table([[hello_p(10)]])
        tables = self.table.split(50, 60)
        self.assertEqual(len(tables), 2)
        top, bottom = [str_p(tbl.rows[0][0]) for tbl in tables]
        self.assertEqual(top, "hello 0 hello 1 hello 2 hello 3 hello 4")
        self.assertEqual(bottom, "hello 5 hello 6 hello 7 hello 8 hello 9")
