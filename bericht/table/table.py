from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import LayoutError


class TableStyle:
    pass


class Table(Flowable):

    def __init__(self, rows):
        super().__init__()
        assert rows, "Cannot create a table with no rows."
        self.rows = rows
        self._heights = None

    def draw(self):
        y = self.height
        for row, height in zip(self.rows, self._heights):
            y -= height
            row.drawOn(self.canv, 0, y)

    def wrap(self, available_width, available_height):
        self.width = available_width
        self.height = 0
        self._heights = []
        for row in self.rows:
            _, height = row.wrapOn(None, available_width, available_height)
            self._heights.append(height)
            self.height += height
        return available_width, self.height

    def split(self, available_width, available_height):
        if self._heights is None:
            self.wrap(available_width, available_height)

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
                    Table(self.rows[:split_at_row+1]),
                    Table(self.rows[split_at_row-1:])
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
            Table(top_rows),
            Table(bottom_rows)
        ]
