from reportlab.platypus.doctemplate import LayoutError

__all__ = ('Block', 'LayoutError')


class Block:

    __slots__ = (
        'tag', 'parent', 'id', 'classes', 'style', 'children',
        'nth', 'nth_type', 'width', 'height',
    )

    def __init__(self, tag, parent, id, classes, style):
        self.tag = tag
        self.parent = parent
        self.id = id
        self.classes = classes
        self.style = style
        self.children = []
        self.width = None
        self.height = None

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self, page, x, y):
        pass

    def split(self, available_width, available_height):
        return []

    def draw_border(self):
        s = self.style
        top_left, top_right, bottom_left, bottom_right = self.border_box
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

    @property
    def empty(self):
        return not self.children

    @property
    def min_content_width(self):
        width = 0
        for block in self.children:
            width = max(width, block.min_content_width)
        return width

    @property
    def frame_top(self):
        s = self.style
        return s.margin_top + s.border_top_width + s.padding_top

    @property
    def frame_right(self):
        s = self.style
        return s.padding_right + s.border_right_width + s.margin_right

    @property
    def frame_bottom(self):
        s = self.style
        return s.margin_bottom + s.border_bottom_width + s.padding_bottom

    @property
    def frame_left(self):
        s = self.style
        return s.margin_left + s.border_left_width + s.padding_left

    @property
    def frame_width(self):
        return self.frame_left + self.frame_right

    @property
    def frame_height(self):
        return self.frame_top + self.frame_bottom

    @property
    def border_box(self):
        s = self.style
        return (
            (s.margin_left, self.height-s.margin_top),  # top left
            (self.width-s.margin_right, self.height-s.margin_top),  # top right
            (s.margin_left, s.margin_bottom),  # bottom left
            (self.width-s.margin_right, s.margin_bottom),  # bottom right
        )
