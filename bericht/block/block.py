from reportlab.platypus.doctemplate import LayoutError

__all__ = ('Block', 'LayoutError')


class Block:

    __slots__ = (
        'content', 'content_widths', 'content_heights',
        'style', 'width', 'height', 'was_split',

        # reportlab stuff
        'canv', '_frame', '_postponed',
    )

    def __init__(self, content, style, was_split=False):
        self.content = content
        self.content_widths = None
        self.content_heights = None
        self.style = style
        self.width = None
        self.height = None
        self.was_split = was_split

    def wrapOn(self, canvas, available_width, available_height):
        self.canv = canvas
        result = self.wrap(available_width, available_height)
        self.canv = None
        return result

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def drawOn(self, canvas, x, y, _sW=None):
        canvas.saveState()
        canvas.translate(x, y)
        self.canv = canvas
        self.draw()
        self.canv = None
        # canvas.setStrokeColor(gray)
        # canvas.rect(0, 0, self.width, self.height)
        canvas.restoreState()

    def draw(self):
        pass

    def splitOn(self, canvas, available_width, available_height):
        self.canv = canvas
        result = self.split(available_width, available_height)
        self.canv = None
        return result

    def split(self, available_width, available_height):
        return []

    def getKeepWithNext(self):
        return False

    def getSpaceBefore(self):
        return 0

    def getSpaceAfter(self):
        return 0

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
        return not self.content

    @property
    def min_content_width(self):
        width = 0
        for block in self.content:
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
