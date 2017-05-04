from reportlab.platypus.paragraph import Paragraph

from .table import Table
from .row import Row
from .cell import Cell, Span

__all__ = ['TableBuilder']


class TableBuilder:

    def __init__(self, rlstyle):
        self.rows = []
        self.rlstyle = rlstyle

    def row(self, *row):
        cells = []
        for col in row:
            if isinstance(col, (Cell, Span)):
                cell = col
            elif isinstance(col, Paragraph):
                cell = Cell([col])
            elif isinstance(col, tuple):
                cell = Cell([Paragraph(col[0], self.rlstyle)])
                for rule in col[1:]:
                    rule(cell.style)
            else:
                cell = Cell([Paragraph(str(col), self.rlstyle)])
            cells.append(cell)
        self.rows.append(Row(cells))

    @property
    def table(self):
        return Table(self.rows)
