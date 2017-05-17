from math import floor
from itertools import chain
from collections import namedtuple
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent
from reportlab.platypus.flowables import Flowable

from ..style import Style, TextAlign

__all__ = ['Paragraph', 'Word', 'Break']


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


class Paragraph(Flowable):

    @classmethod
    def from_string(cls, text, style=None):
        style = style or Style.default()
        words = [Word(style, word) for word in text.split()]
        return cls(words, style)

    def __init__(self, words, style):
        super().__init__()
        self.words = words
        self.style = style
        self.lines = None
        self.widths = None

    def __str__(self):
        return ' '.join(str(w) for w in self.words)

    @property
    def max_width(self):
        return stringWidth(str(self), self.style.font_name, self.style.font_size)

    def draw(self):
        style = self.style
        x, y, alignment = 0, self.height - style.leading, style.text_align
        txt = self.canv.beginText(x, y)
        txt.setFont(style.font_name, style.font_size, style.leading)
        for line, width in zip(self.lines, self.widths):
            if alignment == TextAlign.right:
                txt.setXPos(self.width - width)
            fragments = []
            for word in line:
                if word is Break:
                    continue
                for part in word.parts:
                    if style != part.style:
                        if fragments:
                            txt._textOut(''.join(fragments))
                            fragments = []
                        style = part.style
                        txt._setFont(style.font_name, style.font_size)
                    fragments.append(part.part)
                fragments.append(' ')
            if fragments and fragments[-1] == ' ':
                fragments.pop()  # last space
            txt._textOut(''.join(fragments), True)
        self.canv.drawText(txt)

    def wrap(self, available_width, _=None):
        self.width = available_width
        line = []
        self.lines = [line]
        self.widths = [0]
        if not self.words:
            return 0, 0

        space_width = stringWidth(' ', self.style.font_name, self.style.font_size)
        for word in self.words:

            if word is Break:
                line = [Break]
                self.lines.append(line)
                self.widths.append(0)
                continue

            word_width = word.width
            if self.widths[-1]+word_width > available_width:
                line = []
                self.lines.append(line)
                self.widths.append(0)

            self.widths[-1] += word_width + space_width
            line.append(word)

        self.height = len(self.lines) * self.style.leading
        return available_width, self.height

    def split(self, available_width, available_height):
        lines = floor(available_height / self.style.leading)
        if not lines:
            return []
        elif lines == len(self.lines):
            return [self]
        return (
            Paragraph(list(chain(*self.lines[:lines])), self.style),
            Paragraph(list(chain(*self.lines[lines:])), self.style)
        )
