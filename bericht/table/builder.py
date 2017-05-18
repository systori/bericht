from itertools import zip_longest
from . import *
from ..text import *

__all__ = ('TableBuilder',)


class TableBuilder:

    def __init__(self, ratios, style):
        self.ratios = ratios
        self.columns = [0]*len(ratios)
        self.rows = []
        self.style = style

    def row(self, *row, cell_style=None, row_style=None):
        assert len(row) <= len(self.columns), "Too many cells added to row."
        cell_style = cell_style or self.style
        row_style = row_style or self.style
        cells = []
        for col, _ in zip_longest(row, self.columns):
            if isinstance(col, (Cell, Span)) or col is None:
                cell = col
            elif isinstance(col, (list, tuple)):
                cell = Cell(col, cell_style)
            elif isinstance(col, (Paragraph, Text, Table)):
                cell = Cell((col,), cell_style)
            else:
                cell = Cell((Text(str(col), cell_style),), cell_style)
            cells.append(cell)
        for i, (ratio, width, cell) in enumerate(zip(self.ratios, self.columns, cells)):
            if isinstance(cells[i], Cell) and ratio == 0:
                self.columns[i] = max(
                    width, cell.min_content_width+cell.frame_width
                )
        self.rows.append(Row(cells, row_style))

    @property
    def table(self):
        return Table(self.ratios, self.columns, self.rows, self.style)
