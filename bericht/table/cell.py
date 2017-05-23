from enum import Enum
from bericht.block import Block, LayoutError
from bericht.style import VerticalAlign

__all__ = ('Cell', 'Span')


class Span(Enum):
    col = 1


class Cell(Block):

    __slots__ = ('collapsed', 'first', 'last')

    def __init__(self, words, style, was_split=False):
        super().__init__(words, style, was_split)
        self.collapsed = False

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

    def draw(self):
        x = self.frame_left
        if self.style.vertical_align == VerticalAlign.top:
            y = self.height - self.frame_top
        elif self.style.vertical_align == VerticalAlign.middle:
            y = (self.height + sum(self.content_heights)) / 2.0
        else:
            y = self.frame_bottom + sum(self.content_heights)

        for block, height in zip(self.content, self.content_heights):
            y -= height
            block.drawOn(self.canv, x, y)

    def wrap(self, available_width, _=None):
        self.width = available_width
        self.content_heights = []
        content_width = available_width - self.frame_width
        consumed = 0
        for block in self.content:
            _, height = block.wrapOn(None, content_width, 0)
            consumed += height
            self.content_heights.append(height)
        self.height = self.frame_height + consumed
        return available_width, self.height

    def split(self, available_width, available_height):

        if self.content_heights is None:
            self.wrap(available_width)

        if not self.content_heights:
            return [self]

        if self.style.vertical_align == VerticalAlign.top:
            consumed_height = self.frame_top
        elif self.style.vertical_align == VerticalAlign.middle:
            consumed_height = (self.height - sum(self.content_heights)) / 2.0
        else:
            consumed_height = self.height - (sum(self.content_heights) + self.frame_bottom)

        if consumed_height >= available_height:
            # border and padding don't even fit
            return []

        split_at_block, split_block_height = -1, 0
        for split_at_block, split_block_height in enumerate(self.content_heights):
            consumed_height += split_block_height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.content) == 1 or len(self.content)-1 == split_at_block:
                return [self]
            else:
                return [
                    Cell(self.content[:split_at_block+1], self.style, was_split=True),
                    Cell(self.content[split_at_block-1:], self.style, was_split=True)
                ]

        top_content = list(self.content[:split_at_block])
        block = self.content[split_at_block]
        bottom_content = list(self.content[split_at_block+1:])

        split = block.splitOn(
            None,
            available_width - self.frame_width,
            available_height - (consumed_height - split_block_height)
        )

        if not split:
            # flowable could not be split,
            # move entirely to bottom half
            bottom_content.insert(0, block)
        elif len(split) == 1:
            # flowable completely fits in top half
            top_content.append(block)
        elif len(split) == 2:
            top_content.append(split[0])
            bottom_content.append(split[1])
        else:
            raise LayoutError("Splitting cell with flowable {} produced unexpected result.".format(flowable))

        return [] if not top_content else [
            Cell(top_content, self.style, was_split=True),
            Cell(bottom_content, self.style, was_split=True)
        ]
