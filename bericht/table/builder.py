from . import *
from ..style import *
from ..text import *

__all__ = ('TableBuilder',)


class TableBuilder:

    def __init__(self, style):
        self.rows = []
        self.style = style

    def row(self, *row):
        cells = []
        for col in row:
            if isinstance(col, (Cell, Span)):
                cell = col
            elif isinstance(col, Paragraph):
                cell = Cell([col], self.style)
            elif isinstance(col, str):
                cell = Cell([Paragraph.from_string(col, self.style)], self.style)
            else:
                raise ValueError
            cells.append(cell)
        self.rows.append(Row(cells, self.style))

    @property
    def table(self):
        return Table(self.rows, self.style)
