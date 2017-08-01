from bericht.node import Block
from .style import VerticalAlign
from .cell import Cell

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

    def wrap(self, page, available_width):
        return available_width, (
            self.table.reserve_header_height(page, available_width) +
            self._wrap(page, available_width)[1] +
            self.table.reserve_footer_height(page, available_width)
        )

    def _wrap(self, page, available_width):
        column_widths = self.table.get_column_widths(page, self, available_width)
        self.width = available_width
        cell_widths = self.cell_widths = []

        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)

        if not self.children:
            return 0, 0

        col_width = iter(column_widths)
        for cell in self.children:
            if not cell or cell.colspan == 1:
                cell_widths.append(next(col_width))
            else:
                cell_widths.append(0)
                for col in range(cell.colspan):
                    cell_widths[-1] += next(col_width) + self.cell_spacing / 2.0

        max_height = 0
        for cell, cell_width in zip(self.children, cell_widths):
            if cell is not None:
                cell.collapsed = self.collapsed
                _, height = cell.wrap(page, cell_width)
                max_height = max(max_height, height)

        for cell in self.children:
            if not cell: continue
            cell.height = max_height

        self.height = self.frame_height + max_height
        return self.width, self.height

    def split(self, top_parent, bottom_parent, available_height):
        if available_height >= self.height:
            return self, None

        content_height = available_height - self.frame_height
        top_half = Row(self.tag, self.parent, self.id, self.classes, self.css, self.position)
        bottom_half = Row(self.tag, self.parent, self.id, self.classes, self.css, self.position+1)

        for cell in self.children:
            if cell:
                cell.split(top_half, bottom_half, content_height)

        return top_half, bottom_half

    def draw(self, page, x, y):
        x, y = self.table.draw_header(page, x, y)
        x, y = self._draw(page, x, y)
        return x, y

    def _draw(self, page, x, y):
        original_x, original_y = x, y
        x += self.cell_spacing / 2.0
        #y -= self.height
        y -= self.frame_top
        last = len(self.cell_widths)-1
        for i, (cell, width) in enumerate(zip(self.children, self.cell_widths)):
            if cell:
                if False and self.collapsed:
                    self.draw_collapsed_cell_border(
                        None if i == 0 else self.children[i-1],
                        cell,
                        None if i == last else self.children[i+1],
                    )
                else:
                    cell.draw_border_and_background(page, x, original_y - self.height)
                cell.draw(page, x, y)
            x += width + self.cell_spacing / 2.0
        return original_x, original_y - self.height

    def draw_collapsed_cell_border(self, before, cell, after):
        pass

