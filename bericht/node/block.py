from .style import Style

__all__ = ('Block',)


class Block:

    __slots__ = (
        'tag', 'parent', 'id', 'classes', 'style', 'children',
        'css', 'position', 'last_child', 'width', 'height',
    )

    def __init__(self, tag, parent, id, classes, css, position, children=None):
        self.tag = tag
        self.parent = parent
        self.id = id
        self.classes = classes or []
        self.css = css
        self.position = position
        self.children = children or []
        self.width = None
        self.height = None
        self.last_child = False
        self.style = Style.default()
        if self.parent:
            self.parent.add(self)

    def add(self, child):
        self.children.append(child)

    def wrap(self, page, available_width):
        raise NotImplementedError

    def split(self, available_height):
        raise NotImplementedError

    def draw(self, page, x, y):
        raise NotImplementedError

    def draw_border_and_background(self, page, x, y):
        page.save_state()
        page.translate(x, y)
        s = self.style
        top_left, top_right, bottom_left, bottom_right = self.border_box
        if s.background_color:
            page.fill_color(*s.background_color)
            page.rectangle(0, 0, self.width, self.height)
        if s.border_top_width > 0:
            page.line_width(s.border_top_width)
            page.stroke_color(*s.border_top_color)
            page.line(*top_left, *top_right)
        if s.border_right_width > 0:
            page.line_width(s.border_right_width)
            page.stroke_color(*s.border_right_color)
            page.line(*top_right, *bottom_right)
        if s.border_bottom_width > 0:
            page.line_width(s.border_bottom_width)
            page.stroke_color(*s.border_bottom_color)
            page.line(*bottom_left, *bottom_right)
        if s.border_left_width > 0:
            page.line_width(s.border_left_width)
            page.stroke_color(*s.border_left_color)
            page.line(*top_left, *bottom_left)
        page.restore_state()

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
