from . import *
from ..style import *
from ..text import *

__all__ = ('TableBuilder',)


class TableBuilder:

    def __init__(self, style):
        self.rows = []
        self.style = style
        self.row_style = RowStyle.from_style(style)
        self.cell_style = CellStyle.from_style(style)
        self.p_style = BlockStyle.from_style(style)

    def row(self, *row):
        cells = []
        for col in row:
            if isinstance(col, (Cell, Span)):
                cell = col
            elif isinstance(col, Paragraph):
                cell = Cell([col], self.cell_style)
            elif isinstance(col, str):
                cell = Cell([Paragraph.from_string(col, self.p_style)], self.cell_style)
            else:
                raise ValueError
            cells.append(cell)
        self.rows.append(Row(cells, self.row_style))

    @property
    def table(self):
        return Table(self.rows, self.style)
