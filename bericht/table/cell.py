from enum import Enum
from bericht.block import Block, LayoutError

__all__ = ('Cell', 'Span')


class Span(Enum):
    col = 1


class Cell(Block):

    def __init__(self, flowables, style):
        super().__init__(style)
        self.flowables = flowables
        self._vpos = None
        self._heights = None

    @property
    def max_width(self):
        if self.flowables:
            return self.flowables[0].max_width
        return 0

    def draw(self):
        for flowable, y in zip(self.flowables, self._vpos):
            flowable.drawOn(self.canv, self.content_x, y)
        self.draw_borders()

    def wrap(self, available_width, _=None):
        self.width = available_width
        self._vpos = []
        self._heights = []
        content_width = self.content_width(available_width)
        y = self.content_y
        for flowable in reversed(self.flowables):
            self._vpos.insert(0, y)
            _, consumed = flowable.wrapOn(None, content_width, 0)
            y += consumed
            self._heights.insert(0, consumed)
        self.height = self.total_height(sum(self._heights))
        return available_width, self.height

    def split(self, available_width, available_height):

        if self._vpos is None:
            self.wrap(available_width, 0)

        if not self._vpos:
            return [self]

        consumed_height = 0
        split_at_flowable = -1
        for split_at_flowable, height in enumerate(self._heights):
            consumed_height += height
            if consumed_height >= available_height:
                break

        if consumed_height == available_height:
            if len(self.flowables) == 1 or len(self.flowables)-1 == split_at_flowable:
                return [self]
            else:
                return [
                    Cell(self.flowables[:split_at_flowable+1]),
                    Cell(self.flowables[split_at_flowable-1:])
                ]

        top_flowables = self.flowables[:split_at_flowable]
        flowable = self.flowables[split_at_flowable]
        bottom_flowables = self.flowables[split_at_flowable+1:]

        top_height = available_height - (consumed_height - height)

        split = flowable.splitOn(None, available_width, top_height)

        if not split:
            # flowable could not be split,
            # move entirely to bottom half
            bottom_flowables.insert(0, flowable)
        elif len(split) == 1:
            # flowable completely fits in top half
            top_flowables.append(flowable)
        elif len(split) == 2:
            top_flowables.append(split[0])
            bottom_flowables.append(split[1])
        else:
            raise LayoutError("Splitting cell with flowable {} produced unexpected result.".format(flowable))

        return [] if not top_flowables else [
            Cell(top_flowables, self.style),
            Cell(bottom_flowables, self.style)
        ]
