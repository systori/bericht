from math import floor
from itertools import chain
from string import whitespace
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent
from . import style

__all__ = ('Box', 'Block', 'Inline', 'ListItem')


class StyledPart:
    __slots__ = ('parent', 'style', 'part')

    def __init__(self, parent, style, part):
        self.parent = parent
        self.style = style
        self.part = part

    @property
    def width(self):
        return stringWidth(self.part, self.style.font_name, self.style.font_size)


class Word:
    __slots__ = ('parts',)

    def __init__(self, paragraph, style, word):
        self.parts = [StyledPart(paragraph, style, word)]

    def add(self, paragraph, style, part):
        if self.parts[-1].style != style:
            self.parts.append(StyledPart(paragraph, style, part))
        else:
            self.parts[-1] = StyledPart(paragraph, style, self.parts[-1].part+part)
        return self

    @property
    def width(self):
        return sum(p.width for p in self.parts)

    def __str__(self):
        return ''.join(p.part for p in self.parts)


class Line:

    __slots__ = ('words', 'width')

    def __init__(self, words=None):
        self.words = words or []
        self.width = 0

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

    def add(self, child):
        if self.box.buffered:
            self.box.children.append(child)

    def insert(self, i, child):
        if self.box.buffered:
            self.box.children.insert(i, child)


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
            self.style = style.default
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
    def descendants(self):
        for child in self.children:
            if isinstance(child, str):
                yield child
            else:
                yield from child.text

    @property
    def first(self):
        return self.position == 1

    @property
    def first_of_type(self):
        return self.position_of_type == 1

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

    def wrap(self, page, available_width):
        self.width = available_width
        self.height = 0

        if not self.children:
            return 0, 0

        line = None

        max_width = 0
        space_width = stringWidth(' ', self.style.font_name, self.style.font_size)
        for child in self.children:

            if isinstance(child, str):
                for part in word.parts:
                    part.style = part.style.inherit(self.style)

                word_width = word.width
                if line.width+word_width > available_width:
                    if line:
                        line = Line()
                        lines.append(line)

                line.width += word_width + space_width
                line.add(word)
                max_width = max(line.width, max_width)

            elif child.tag == 'br':
                if not line:
                    line = Line()
                line.add(child)
                self.lines.append(line)
                line = None
                continue

            else:
                if line:
                    self.lines.append(line)
                    line = None
                self.lines.append(child)
                continue

        self.height = self.frame_height + len(lines) * self.style.leading
        return max_width, self.height

    def split(self, top_container, bottom_container, available_height):
        lines = floor(available_height / self.style.leading)
        if lines == len(self.children):
            self.parent = top_container
            top_container.children.append(self)
            return self, None
        else:
            top = Paragraph(self.tag, top_container, self.id, self.classes, self.css, self.position)
            top.words = list(chain(*self.children[:lines]))
            bottom = Paragraph(self.tag, bottom_container, self.id, self.classes, self.css, self.position)
            bottom.words = list(chain(*self.children[lines:]))
            return top, bottom

    def draw(self, page, x, y):
        final_x, final_y = x, y - self.height
        style = self.style
        txt = page.begin_text(final_x, final_y)
        x, y, alignment = 0, self.height - style.leading, style.text_align
        txt.set_position(x, y)
        txt.set_font(style.font_name, style.font_size, style.leading)
        for line in self.children:
            if self.style.text_align == TextAlign.right:
                txt.set_position(self.width - line.width)
            elif self.style.text_align == TextAlign.center:
                txt.set_position((self.width - line.width) / 2.0)
            fragments = []
            for word in line.words:
                if word is Break:
                    continue
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
        txt.close()
        return final_x, final_y
