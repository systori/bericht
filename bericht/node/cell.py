from enum import Enum
from bericht.node import Block
from .style import VerticalAlign

__all__ = ('Cell',)


class Cell(Block):

    __slots__ = ('collapsed', 'first', 'last', 'content_heights', 'colspan')

    def __init__(self, *args, colspan=1):
        super().__init__(*args)
        self.collapsed = False
        self.content_heights = None
        self.colspan = colspan

    @property
    def frame_top(self):
        s = self.style
        if self.collapsed:
            return s.border_top_width/2 + s.padding_top
        else:
            return s.border_top_width + s.padding_top

    @property
    def frame_right(self):
        s = self.style
        if self.collapsed:
            return s.padding_right + s.border_right_width/2.0
        else:
            return s.padding_right + s.border_right_width

    @property
    def frame_bottom(self):
        s = self.style
        if self.collapsed:
            return s.border_bottom_width/2.0 + s.padding_bottom
        else:
            return s.border_bottom_width + s.padding_bottom

    @property
    def frame_left(self):
        s = self.style
        if self.collapsed:
            return s.border_left_width/2.0 + s.padding_left
        else:
            return s.border_left_width + s.padding_left

    @property
    def border_box(self):
        return (
            (0, self.height),  # top left
            (self.width, self.height),  # top right
            (0, 0),  # bottom left
            (self.width, 0),  # bottom right
        )

    def draw(self, page, x, y):
        x += self.frame_left
        if self.style.vertical_align == VerticalAlign.top:
            y -= self.frame_top
        elif self.style.vertical_align == VerticalAlign.middle:
            y -= (self.height + sum(self.content_heights)) / 2.0
        else:
            y -= self.height - (sum(self.content_heights) + self.frame_bottom)

        for block, height in zip(self.children, self.content_heights):
            block.draw(page, x, y)
            y -= height

    def wrap(self, page, available_width):
        self.width = available_width
        self.content_heights = []

        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)

        content_width = available_width - self.frame_width

        consumed = 0
        for block in self.children:
            _, height = block.wrap(page, content_width)
            consumed += height
            self.content_heights.append(height)

        self.height = self.frame_height + consumed
        return available_width, self.height

    def split(self, top_parent, bottom_parent, available_height):

        if not self.content_heights:
            self.parent = top_parent
            top_parent.children.append(self)
            bottom_parent.children.append(None)
            return

        if self.style.vertical_align == VerticalAlign.top:
            consumed_height = self.frame_top
        elif self.style.vertical_align == VerticalAlign.middle:
            consumed_height = (self.height - sum(self.content_heights)) / 2.0
        else:
            consumed_height = self.height - (sum(self.content_heights) + self.frame_bottom)

        if consumed_height >= available_height:
            # border and padding don't even fit
            top_parent.children.append(None)
            self.parent = bottom_parent
            bottom_parent.children.append(self)
            return

        split_at_block, split_block_height = -1, 0
        for split_at_block, split_block_height in enumerate(self.content_heights):
            consumed_height += split_block_height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.children) == 1 or len(self.children)-1 == split_at_block:
                self.parent = top_parent
                top_parent.children.append(self)
                bottom_parent.children.append(None)
                return
            else:
                top_cell = Cell(self.tag, top_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)
                for top_child in self.children[:split_at_block+1]:
                    top_child.parent = top_cell
                    top_cell.children.append(top_child)
                bottom_cell = Cell(self.tag, bottom_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)
                for bottom_child in self.children[split_at_block-1:]:
                    bottom_child.parent = bottom_cell
                    bottom_cell.children.append(bottom_child)
                return top_cell, bottom_cell

        top_cell = Cell(self.tag, top_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)
        for top_child in self.children[:split_at_block]:
            top_child.parent = top_cell
            top_cell.children.append(top_child)

        block = self.children[split_at_block]
        bottom_cell = Cell(self.tag, bottom_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)

        block.split(top_cell, bottom_cell, available_height - (consumed_height - split_block_height))

        for bottom_child in self.children[split_at_block+1:]:
            bottom_child.parent = bottom_cell
            bottom_cell.children.append(bottom_child)

        return top_cell, bottom_cell
