from math import floor
from itertools import chain
from collections import namedtuple
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent

from bericht.node import Block
from .style import TextAlign

__all__ = (
    'Paragraph', 'Word', 'Break',
)


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


class Break:
    pass


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


class Paragraph(Block):

    __slots__ = ('words',)

    def __init__(self, *args):
        super().__init__(*args)
        self.words = []

    def __str__(self):
        return ' '.join(str(word) for word in self.words)

    @property
    def min_content_width(self):
        return 0

    def wrap(self, page, available_width):
        self.width = available_width
        self.height = 0
        line = Line()
        lines = self.children = [line]
        if not self.words:
            return 0, 0

        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)

        max_width = 0
        space_width = stringWidth(' ', self.style.font_name, self.style.font_size)
        for word in self.words:

            if word is Break:
                line = Line([Break])
                lines.append(line)
                continue

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
