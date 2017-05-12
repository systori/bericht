from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import LayoutError
from .cell import Cell
from ..style import RowStyle, VerticalAlign, Span

__all__ = ('Row',)


class Row(Flowable):

    def __init__(self, cells, style):
        super().__init__()
        self.cells = cells
        self._widths = None
        self.style = style

    @property
    def columns(self):
        return filter(lambda c: c != Span.col, self.cells)

    def draw(self):
        x = 0
        for cell, width in zip(self.columns, self._widths):
            if isinstance(cell, Span):
                continue
            y = 0
            if cell.style.vertical_align == VerticalAlign.top:
                y = self.height - cell.height
            if cell:
                cell.drawOn(self.canv, x, y)
            x += width

    def wrap(self, available_width, available_height):
        self.width = available_width
        self.height = 0
        self._widths = []

        if not self.cells:
            return 0, 0

        cell_width = float(available_width) / len(self.cells)

        for cell in self.cells:
            if cell == Span.col:
                self._widths[-1] += cell_width
            else:
                self._widths.append(cell_width)

        for cell, width in zip(self.columns, self._widths):
            if cell is None or isinstance(cell, Span):
                continue
            elif isinstance(cell, Cell):
                _, height = cell.wrapOn(None, width, available_height)
                self.height = max(self.height, height)
            else:
                raise ValueError('Row cells must be either None, Span or Cell.')

        return available_width, self.height

    def split(self, available_width, available_height):

        if self._widths is None:
            self.wrap(available_width, available_height)

        if available_height >= self.height:
            return [self]

        top_half = []
        bottom_half = []

        for cell, width in zip(self.columns, self._widths):

            if cell is None:
                top_half.append(None)
                bottom_half.append(None)
                continue

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

        return [] if not any(top_half) else [
            Row(top_half, self.style),
            Row(bottom_half, self.style)
        ]

