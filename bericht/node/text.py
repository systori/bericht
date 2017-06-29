from math import floor
from itertools import chain
from collections import namedtuple
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent

from bericht.node import Block
from .style import Style, TextAlign

__all__ = (
    'Text', 'Paragraph', 'Word', 'Break',
    'para', 'static',
)


def para(text, style=None):
    return Paragraph.from_string(text, style or Style.default())


def static(text, style=None):
    return Text(text, style or Style.default())


class StyledPart(namedtuple('_StyledPart', ('style', 'part'))):

    @property
    def width(self):
        return stringWidth(self.part, self.style.font_name, self.style.font_size)


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


class Paragraph(Block):

    __slots__ = ('words', 'styles', 'word_open')

    def __init__(self, *args):
        super().__init__(*args)
        self.words = []
        self.styles = [self.style]
        self.word_open = False
        if self.parent:
            self.parent.children.append(self)

    def __str__(self):
        return ' '.join(str(word) for word in self.words)

    @property
    def min_content_width(self):
        return 0

    def draw(self, page, x, y):
        style = self.style
        txt = page.begin_text(x, y)
        x, y, alignment = 0, self.height - style.leading, style.text_align
        txt.set_position(x, y)
        #txt.setFont(style.font_name, style.font_size, style.leading)
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
                            txt.line(''.join(fragments))
                            fragments = []
                        style = part.style
                        #txt._setFont(style.font_name, style.font_size)
                    fragments.append(part.part)
                fragments.append(' ')
            if fragments and fragments[-1] == ' ':
                fragments.pop()  # last space
            txt.line(''.join(fragments), True)
        txt.close()

    def wrap(self, page, available_width):
        self.width = available_width
        line = Line()
        lines = self.children = [line]
        if not self.words:
            return 0, 0

        max_width = 0
        space_width = stringWidth(' ', self.style.font_name, self.style.font_size)
        for word in self.words:

            if word is Break:
                line = Line([Break])
                lines.append(line)
                continue

            word_width = word.width
            if line.width+word_width > available_width:
                if line:
                    line = Line()
                    lines.append(line)

            line.width += word_width + space_width
            line.add(word)
            max_width = max(line.width, max_width)

        self.height = len(lines) * self.style.leading
        return max_width, self.height

    def split(self, available_width, available_height):
        lines = floor(available_height / self.style.leading)
        if not lines:
            return []
        elif lines == len(self.content):
            return [self]
        return (
            Paragraph(list(chain(*self.content[:lines])), self.style),
            Paragraph(list(chain(*self.content[lines:])), self.style)
        )


class Text:
    """
    Memory efficient and faster text container without
    word wrapping or granular styling. Has a fixed
    width and height.
    """

    __slots__ = ('text', 'text_width', 'style', 'width', 'height', 'canv')

    def __init__(self, text, style):
        self.text = text
        self.style = style
        self.text_width = stringWidth(text, style.font_name, style.font_size)
        self.width = None
        self.height = style.leading

    @property
    def min_content_width(self):
        return self.text_width

    def wrapOn(self, canvas, available_width, available_height):
        self.width = available_width
        return self.text_width, self.height

    def drawOn(self, canvas, x, y):
        canvas.saveState()
        canvas.translate(x, y)
        self.canv = canvas
        self.draw()
        self.canv = None
        canvas.restoreState()

    def draw(self):
        x = 0
        if self.style.text_align == TextAlign.right:
            x = self.width - self.text_width
        elif self.style.text_align == TextAlign.center:
            x = (self.width - self.text_width) / 2.0
        t = self.canv.beginText(x, 0)
        t._setFont(self.style.font_name, self.style.font_size)
        t._textOut(self.text)
        self.canv.drawText(t)

    def splitOn(self, canvas, available_width, available_height):
        return []