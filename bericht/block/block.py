from reportlab.platypus.doctemplate import LayoutError

__all__ = ('Block', 'LayoutError')


class Block:

    __slots__ = (
        'content', 'content_widths', 'content_heights',
        'style', 'canvas', 'width', 'height', 'was_split',
    )

    def __init__(self, content, style, was_split=False):
        self.content = content
        self.content_widths = None
        self.content_heights = None
        self.style = style
        self.canvas = None
        self.width = None
        self.height = None
        self.was_split = was_split

    def wrapOn(self, canvas, available_width, available_height):
        self.canvas = canvas
        result = self.wrap(available_width, available_height)
        self.canvas = None
        return result

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def drawOn(self, canvas, x, y):
        canvas.saveState()
        canvas.translate(x, y)
        self.canvas = canvas
        self.draw()
        self.canvas = None
        # canvas.setStrokeColor(gray)
        # canvas.rect(0, 0, self.width, self.height)
        canvas.restoreState()

    def draw(self):
        pass

    def splitOn(self, canvas, available_width, available_height):
        self.canvas = canvas
        result = self.split(available_width, available_height)
        self.canvas = None
        return result

    def split(self, available_width, available_height):
        return []

    def draw_borders(self):
        s = self.style
        top_left, top_right, bottom_left, bottom_right = (
            (s.margin_left, self.height-s.margin_top),
            (self.width-s.margin_right, self.height-s.margin_top),
            (s.margin_left, s.margin_bottom),
            (self.width-s.margin_right, s.margin_bottom),
        )
        if s.border_top_width > 0:
            self.canvas.setLineWidth(s.border_top_width)
            self.canvas.setStrokeColor(s.border_top_color)
            self.canvas.line(*top_left, *top_right)
        if s.border_right_width > 0:
            self.canvas.setLineWidth(s.border_right_width)
            self.canvas.setStrokeColor(s.border_right_color)
            self.canvas.line(*top_right, *bottom_right)
        if s.border_bottom_width > 0:
            self.canvas.setLineWidth(s.border_bottom_width)
            self.canvas.setStrokeColor(s.border_bottom_color)
            self.canvas.line(*bottom_left, *bottom_right)
        if s.border_left_width > 0:
            self.canvas.setLineWidth(s.border_left_width)
            self.canvas.setStrokeColor(s.border_left_color)
            self.canvas.line(*top_left, *bottom_left)

    @property
    def max_content_width(self):
        width = 0
        for block in self.content:
            width = max(width, block.max_content_width)
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
