from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import LayoutError


__all__ = ['Table']


class Table(Flowable):

    def __init__(self, columns, rows, style):
        super().__init__()
        self.columns = columns
        self.rows = rows
        self.style = style
        self._widths = None
        self._heights = None

    def draw(self):
        y = self.height
        for row, height in zip(self.rows, self._heights):
            y -= height
            row.drawOn(self.canv, 0, y)

    def fill_stretch_column(self, available_width):
        stretch_cols = self.columns.count(0)
        if stretch_cols > 0:
            fixed_width = sum(self.columns)
            stretch_width = available_width - fixed_width
            stretch_col_width = stretch_width / stretch_cols
            self._widths = [stretch_col_width if w == 0 else w for w in self.columns]
        else:
            self._widths = self.columns.copy()

    def wrap(self, available_width, _=None):
        self.fill_stretch_column(available_width)
        self.width = available_width
        self.height = 0
        self._heights = []
        for row in self.rows:
            _, height = row.wrapOn(None, self._widths, 0)
            self._heights.append(height)
            self.height += height
        return available_width, self.height

    def split(self, available_width, available_height):
        if self._heights is None:
            self.wrap(available_width, 0)

        assert self._heights, "Split called on empty table."

        split_at_row = -1
        split_row_height = 0
        consumed_height = 0
        for height in self._heights:
            split_at_row += 1
            split_row_height = height
            consumed_height += height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.rows) == 1 or len(self.rows)-1 == split_at_row:
                # nothing to split
                return [self]
            else:
                # table split cleanly between rows, no need to further split any rows/cells
                return [
                    Table(self.columns, self.rows[:split_at_row+1], self.style),
                    Table(self.columns, self.rows[split_at_row-1:], self.style)
                ]

        top_rows = self.rows[:split_at_row]
        row = self.rows[split_at_row]
        bottom_rows = self.rows[split_at_row+1:]

        top_height = available_height - (consumed_height - split_row_height)
        split = row.splitOn(None, available_width, top_height)

        if not split:
            # cell could not be split,
            # move entirely to bottom half
            bottom_rows.insert(0, row)
        elif len(split) == 1:
            # cell completely fits in top half,
            # add placeholder to bottom half
            top_rows.append(row)
        elif len(split) == 2:
            top_rows.append(split[0])
            bottom_rows.insert(0, split[1])
        else:
            raise LayoutError("Splitting row {} produced unexpected result.".format(split_at_row))

        return [] if not top_rows else [
            Table(self.columns, top_rows, self.style),
            Table(self.columns, bottom_rows, self.style)
        ]
