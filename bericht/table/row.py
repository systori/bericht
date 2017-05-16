from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import LayoutError
from .cell import Cell, Span
from ..style import VerticalAlign

__all__ = ('Row',)


class Row(Flowable):

    def __init__(self, columns, style):
        super().__init__()
        self.columns = columns
        self.column_widths = None
        self.column_count = len(columns)
        self.cells = None
        self.cell_widths = None
        self.style = style

    def draw(self):
        x = 0
        for cell, width in zip(self.cells, self.cell_widths):
            if cell:
                y = 0
                if cell.style.vertical_align == VerticalAlign.top:
                    y = self.height - cell.height
                cell.drawOn(self.canv, x, y)
            x += width

    def wrap(self, column_widths, _=None):
        assert self.column_count == len(column_widths)
        self.column_widths = column_widths
        self.width = sum(column_widths)
        self.height = 0
        self.cells = []
        self.cell_widths = []

        if not self.columns:
            return 0, 0

        for column, col_width in zip(self.columns, self.column_widths):
            if column == Span.col:
                self.cell_widths[-1] += col_width
            else:
                self.cell_widths.append(col_width)
                self.cells.append(column)

        for cell, cell_width in zip(self.cells, self.cell_widths):
            if cell is not None:
                _, height = cell.wrapOn(None, cell_width, 0)
                self.height = max(self.height, height)

        return self.width, self.height

    def split(self, column_widths, available_height):

        if self.cells is None:
            self.wrap(column_widths)

        if available_height >= self.height:
            return [self]

        top_half = []
        bottom_half = []

        column_idx = 0
        for cell, width in zip(self.cells, self.cell_widths):

            if cell is None:

                top_half.append(None)
                bottom_half.append(None)

            else:

                height = available_height
                if cell.style.vertical_align == VerticalAlign.bottom:
                    height = available_height - (self.height - cell.height)

                split = cell.splitOn(None, width, height)

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

            # self.cells does not include Span.col, so we need to add it back in
            while column_idx+1 < self.column_count and self.columns[column_idx+1] == Span.col:
                top_half.append(Span.col)
                bottom_half.append(Span.col)
                column_idx += 1

            column_idx += 1

        cells_empty = all(c in (None, Span.col) for c in top_half)

        return [] if cells_empty else [
            Row(top_half, self.style),
            Row(bottom_half, self.style)
        ]

