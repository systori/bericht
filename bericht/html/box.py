from math import floor
from itertools import chain, tee
from string import whitespace
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent
from .style import TextAlign, default as default_style

__all__ = ('Box', 'Block', 'Inline', 'ListItem')


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def flatten(sub):
    for line in sub:
        if isinstance(line, Line):
            yield from line.words
        else:
            yield line


class StyledPart:
    __slots__ = ('style', 'part')

    def __init__(self, style, part):
        self.style = style
        self.part = part

    @property
    def width(self):
        return stringWidth(self.part, self.style.font_name, self.style.font_size)

    @property
    def height(self):
        return self.style.leading


SPACE_WIDTH_CACHE = {}


class Word:
    __slots__ = ('parts',)

    def __init__(self, style, word):
        self.parts = [StyledPart(style, word)]

    def add(self, style, part):
        if self.parts[-1].style != style:
            self.parts.append(StyledPart(style, part))
        else:
            self.parts[-1] = StyledPart(style, self.parts[-1].part+part)
        return self

    @property
    def width(self):
        return sum(p.width for p in self.parts)

    @property
    def height(self):
        return max(p.height for p in self.parts)

    @property
    def space_width(self):
        args = (self.parts[-1].style.font_name, self.parts[-1].style.font_size)
        if args not in SPACE_WIDTH_CACHE:
            SPACE_WIDTH_CACHE[args] = stringWidth(' ', *args)
        return SPACE_WIDTH_CACHE[args]

    def __str__(self):
        return ''.join(p.part for p in self.parts)


class Line:

    __slots__ = ('words', 'width', 'height')

    def __init__(self, words=None):
        self.words = words or []
        self.width = 0
        self.height = 0

    def add(self, word):
        self.words.append(word)

    @property
    def empty(self):
        return not self.words

    def __iter__(self):
        return iter(self.words)


class Behavior:
    __slots__ = ('box',)

    def __init__(self, box):
        self.box = box

    @property
    def text_allowed(self):
        return True

    def add(self, child):
        if self.box.buffered:
            self.box.children.append(child)

    def insert(self, i, child):
        if self.box.buffered:
            self.box.children.insert(i, child)

    def wrap(self, page, available_width):
        self.box.width = available_width
        self.box.height = 0

        line = None
        self.box.lines = lines = []

        max_width = 0
        for box in self.box.boxes:

            if isinstance(box, Word):

                word_width = box.width
                if not line or line.width+word_width > available_width:
                    # no line or line is full, start new line
                    line = Line()
                    lines.append(line)

                line.width += word_width + box.space_width
                line.height = max(box.height, line.height)
                max_width = max(line.width, max_width)
                line.add(box)

            elif box.tag == 'br':
                # br is added to current line and starts new line
                if not line:
                    line = Line()
                    lines.append(line)
                box.wrap(page, available_width)
                line.height = max(box.height, line.height)
                line.add(box)
                line = None

            else:
                # block elements take up their own line
                line = None
                box.wrap(page, available_width)
                lines.append(box)

        content_height = sum(b.height for b in lines)
        if self.box.tag == 'br':
            content_height = self.box.style.leading

        self.box.height = self.box.frame_height + content_height

        return max_width, self.box.height

    def split(self, top_container, bottom_container, available_height):
        lines = floor(available_height / self.box.style.leading)
        if lines == len(self.box.children):
            self.box.parent = top_container
            top_container.children.append(self)
            return self, None
        else:
            top = Box(top_container, self.box.tag, self.box.attrs)
            top.position = self.box.position
            top.position_of_type = self.box.position
            top.children = list(flatten(self.box.lines[:lines]))
            bottom = Box(bottom_container, self.box.tag, self.box.attrs)
            bottom.position = self.box.position
            bottom.position_of_type = self.box.position
            bottom.children = list(flatten(self.box.lines[lines:]))
            return top, bottom

    def draw(self, page, x, y):
        final_x, final_y = x, y - self.box.height
        style = self.box.style
        width = self.box.width
        txt = page.begin_text(final_x, final_y)
        x, y, alignment = 0, self.box.height - style.leading, style.text_align
        txt.set_position(x, y)
        txt.set_font(style.font_name, style.font_size, style.leading)
        for line in self.box.lines:
            if isinstance(line, Line):
                if style.text_align == TextAlign.right:
                    txt.set_position(width - line.width)
                elif style.text_align == TextAlign.center:
                    txt.set_position((width - line.width) / 2.0)
                fragments = []
                for word in line.words:
                    if isinstance(word, Word):
                        for part in word.parts:
                            if style != part.style:
                                if fragments:
                                    txt.draw(''.join(fragments))
                                    fragments = []
                                style = part.style
                                txt.set_font(style.font_name, style.font_size, style.leading)
                            fragments.append(part.part)
                        fragments.append(' ')
                if fragments and fragments[-1] == ' ':
                    fragments.pop()  # last space
                txt.draw(''.join(fragments), new_line=True)
            else:
                line.draw(page, final_x, final_y + y)
            y -= line.height
        txt.close()
        return final_x, final_y


class Block(Behavior):
    __slots__ = ()


class Inline(Behavior):
    __slots__ = ()


class ListItem(Behavior):
    __slots__ = ()


class Box:

    __slots__ = (
        'parent', 'tag', 'attrs', 'id', 'classes', 'style', 'behavior', 'buffered',
        'position', 'last', 'position_of_type', 'last_of_type', 'width', 'height',
        'children', 'lines', 'before', 'after'
    )

    def __init__(self, parent, tag, attrs):
        self.parent = parent
        self.tag = tag
        self.attrs = attrs
        self.id = attrs.get('id', None)
        self.classes = attrs.get('class', [])

        if parent is None:
            self.style = default_style
        else:
            self.style = parent.style.inherit()

        self.behavior = None

        self.position = 1
        self.position_of_type = 1
        self.last = False

        self.width = None
        self.height = None

        self.children = []
        self.lines = []

        self.before = None
        self.after = None

        self.buffered = True

    def __str__(self):
        return '{}: <{}>'.format(self.behavior.__class__.__name__, self.tag)

    @property
    def first(self):
        return self.position == 1

    @property
    def first_of_type(self):
        return self.position_of_type == 1

    @property
    def text_allowed(self):
        return self.behavior.text_allowed

    def add(self, child):
        self.behavior.add(child)

    def insert(self, i, child):
        self.behavior.insert(i, child)

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

    @property
    def min_content_width(self):
        return 0

    def traverse(self):
        for child in self.children:
            if isinstance(child, str):
                yield child, self
            elif child.style.display == 'inline' and not child.tag == 'br':
                yield from child.traverse()
            else:
                yield child, self

    @property
    def boxes(self):
        words = []
        word_open = False
        for box, parent in self.traverse():
            if isinstance(box, str):
                if box[0] in whitespace:
                    word_open = False
                parts = box.split()
                if not parts:
                    continue
                word_iter = iter(parts)
                if word_open:
                    words[-1].add(parent.style, next(word_iter))
                words.extend(Word(parent.style, word) for word in word_iter)
                word_open = box[-1] not in whitespace
            else:
                if words:
                    yield from words
                    words = []
                    word_open = False
                yield box
        if words:
            yield from words

    def wrap(self, page, available_width):
        return self.behavior.wrap(page, available_width)

    def split(self, top_container, bottom_container, available_height):
        return self.behavior.split(top_container, bottom_container, available_height)

    def draw(self, page, x, y):
        return self.behavior.draw(page, x, y)
