from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import LayoutError

__all__ = ('Cell',)


class Cell(Flowable):

    def __init__(self, flowables, style):
        super().__init__()
        self.flowables = flowables
        self._vpos = None
        self._heights = None
        self.style = style

    def draw(self):
        for flowable, y in zip(self.flowables, self._vpos):
            flowable.drawOn(self.canv, 0, y)
        self.draw_borders()

    def draw_borders(self):
        if self.style.border_top_width > 0:
            self.canv.setStrokeColor(self.style.border_top_color)
            self.canv.line(0, self.height, self.width, self.height)
        if self.style.border_right_width > 0:
            self.canv.setStrokeColor(self.style.border_right_color)
            self.canv.line(self.width, self.height, self.width, 0)
        if self.style.border_bottom_width > 0:
            self.canv.setStrokeColor(self.style.border_bottom_color)
            self.canv.line(0, 0, self.width, 0)
        if self.style.border_left_width > 0:
            self.canv.setStrokeColor(self.style.border_left_color)
            self.canv.line(0, self.height, 0, 0)

    def wrap(self, available_width, available_height):
        self.width = available_width
        self.height = 0
        self._vpos = []
        self._heights = []
        for flowable in reversed(self.flowables):
            self._vpos.insert(0, self.height)
            _, height = flowable.wrapOn(None, available_width, available_height)
            consumed = flowable.getSpaceBefore() + height + flowable.getSpaceAfter()
            self.height += consumed
            self._heights.insert(0, consumed)
        return available_width, self.height

    def split(self, available_width, available_height):

        if self._vpos is None:
            self.wrap(available_width, available_height)

        assert self._vpos, "Split called on empty cell."

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
