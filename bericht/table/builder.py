from itertools import zip_longest
from . import *
from ..text import *

__all__ = ('TableBuilder',)


class TableBuilder:

    def __init__(self, columns, style):
        self._maximums = columns.copy()
        self.columns = columns
        self.rows = []
        self.style = style

    def row(self, *row, cell_style=None, row_style=None):
        cell_style = cell_style or self.style
        row_style = row_style or self.style
        cells = []
        for col, _ in zip_longest(row, self.columns):
            if isinstance(col, (Cell, Span)) or col is None:
                cell = col
            elif isinstance(col, list):
                cell = Cell(col, cell_style)
            elif isinstance(col, Paragraph):
                cell = Cell([col], cell_style)
            elif isinstance(col, str):
                cell = Cell([Paragraph.from_string(col, cell_style)], cell_style)
            else:
                raise ValueError
            cells.append(cell)
        for i, column in enumerate(self.columns):
            if column != 0 and isinstance(cells[i], Cell):
                self._maximums[i] = max(self._maximums[i], cells[i].max_width)
        self.rows.append(Row(cells, row_style))

    @property
    def table(self):
        return Table(self._maximums, self.rows, self.style)
