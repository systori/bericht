from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import LayoutError

__all__ = ('Block', 'LayoutError')


class Block(Flowable):

    def __init__(self, style):
        super().__init__()
        self.style = style

    @property
    def content_x(self):
        s = self.style
        return s.margin_left + s.border_left_width + s.padding_left

    @property
    def content_y(self):
        s = self.style
        return s.margin_bottom + s.border_bottom_width + s.padding_bottom

    @property
    def content_top_offset(self):
        s = self.style
        return s.margin_top + s.border_top_width + s.padding_top

    def content_width(self, total_width):
        s = self.style
        return total_width - (
            s.margin_left + s.border_left_width + s.padding_left +
            s.margin_right + s.border_right_width + s.padding_right
        )

    def total_height(self, content_height):
        s = self.style
        return (
            s.margin_top + s.border_top_width + s.padding_top +
            content_height +
            s.margin_bottom + s.border_bottom_width + s.padding_bottom
        )

    def draw_borders(self):
        s = self.style
        top_left, top_right, bottom_left, bottom_right = (
            (s.margin_left, self.height-s.margin_top),
            (self.width-s.margin_right, self.height-s.margin_top),
            (s.margin_left, s.margin_bottom),
            (self.width-s.margin_right, s.margin_bottom),
        )
        if s.border_top_width > 0:
            self.canv.setLineWidth(s.border_top_width)
            self.canv.setStrokeColor(s.border_top_color)
            self.canv.line(*top_left, *top_right)
        if s.border_right_width > 0:
            self.canv.setLineWidth(s.border_right_width)
            self.canv.setStrokeColor(s.border_right_color)
            self.canv.line(*top_right, *bottom_right)
        if s.border_bottom_width > 0:
            self.canv.setLineWidth(s.border_bottom_width)
            self.canv.setStrokeColor(s.border_bottom_color)
            self.canv.line(*bottom_left, *bottom_right)
        if s.border_left_width > 0:
            self.canv.setLineWidth(s.border_left_width)
            self.canv.setStrokeColor(s.border_left_color)
            self.canv.line(*top_left, *bottom_left)
