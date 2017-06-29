from bericht.node import Block, LayoutError
from .style import VerticalAlign
from .cell import Cell, Span

__all__ = ('Row',)


class Row(Block):

    __slots__ = (
        'collapsed', 'cell_widths', 'cell_spacing',
    )

    def __init__(self, *args):
        super().__init__(*args)
        self.collapsed = False
        self.cell_widths = []
        self.cell_spacing = 0
        if self.parent.tag in ('thead', 'tfoot'):
            self.parent.children.append(self)

    @property
    def table(self):
        return self.parent.parent

    @property
    def frame_top(self):
        if self.collapsed:
            return self.style.border_top_width
        return 0

    @property
    def frame_right(self):
        return 0

    @property
    def frame_bottom(self):
        if self.collapsed:
            return self.style.border_bottom_width
        return 0

    @property
    def frame_left(self):
        return 0

    def draw(self, page, x, y, header_draw=True):
        if header_draw and self.table.thead and self.table.thead.drawn_on != page.page_number:
            y = self.table.thead.draw(page, x, y)
        x += self.cell_spacing / 2.0
        y -= self.height
        y += self.frame_bottom
        last = len(self.cell_widths)-1
        for i, (cell, width) in enumerate(zip(self.children, self.cell_widths)):
            cell.draw(page, x, y)
            if False and self.collapsed:
                self.draw_collapsed_cell_border(
                    None if i == 0 else self.children[i-1],
                    cell,
                    None if i == last else self.children[i+1],
                )
            else:
                cell.draw_border()
            x += width + self.cell_spacing / 2.0

    def draw_collapsed_cell_border(self, before, cell, after):
        pass

    def wrap(self, page, available_width, header_wrap=True):

        head_height = 0
        if header_wrap and self.table.thead and self.table.thead.drawn_on != page.page_number:
            head_height = self.table.thead.wrap(page, available_width)[1]

        column_widths = self.table.get_column_widths(page, self, available_width)
        self.width = available_width
        cell_widths = self.cell_widths = []

        if not self.children:
            return 0, 0

        for column, col_width in zip(self.children, column_widths):
            if column == Span.col:
                cell_widths[-1] += col_width + self.cell_spacing / 2.0
            else:
                cell_widths.append(col_width)

        max_height = 0
        for cell, cell_width in zip(self.children, cell_widths):
            if cell is not None:
                cell.collapsed = self.collapsed
                _, height = cell.wrap(page, cell_width)
                max_height = max(max_height, height)

        for cell in self.children:
            cell.height = max_height

        self.height = self.frame_height + max_height
        return self.width, self.height + head_height

    def split(self, available_width, available_height):

        if self.content is None:
            self.wrap(available_width)

        if available_height >= self.height:
            return [self]

        content_height = available_height - self.frame_height
        top_half = []
        bottom_half = []

        column_idx = 0
        for cell, width in zip(self.content, self.content_widths):

            split = cell.splitOn(None, width, content_height)

            if not split:
                # cell could not be split,
                # move entirely to bottom half
                top_half.append(Cell([], cell.style))
                bottom_half.append(cell)
            elif len(split) == 1:
                # cell completely fits in top half,
                # add placeholder to bottom half
                top_half.append(cell)
                bottom_half.append(Cell([], cell.style))
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

        cells_empty = all(c == Span.col or c.empty for c in top_half)

        return [] if cells_empty else [
            Row(top_half, self.style, was_split=True),
            Row(bottom_half, self.style, was_split=True)
        ]

