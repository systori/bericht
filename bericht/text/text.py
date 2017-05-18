from math import floor
from itertools import chain
from collections import namedtuple
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent

from bericht.block import Block
from bericht.style import Style, TextAlign

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


class Paragraph(Block):

    __slots__ = ('words',)

    @classmethod
    def from_string(cls, text, style=None):
        style = style or Style.default()
        words = [Word(style, word) for word in text.split()]
        return cls(words, style)

    def __init__(self, words, style):
        super().__init__([], style)
        self.words = words

    def __str__(self):
        return ' '.join(str(word) for word in self.words)

    @property
    def max_content_width(self):
        return stringWidth(str(self), self.style.font_name, self.style.font_size)

    def draw(self):
        style = self.style
        x, y, alignment = 0, self.height - style.leading, style.text_align
        txt = self.canvas.beginText(x, y)
        txt.setFont(style.font_name, style.font_size, style.leading)
        for line, width in zip(self.content, self.content_widths):
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
        lines = self.content = [line]
        widths = self.content_widths = [0]
        if not self.content:
            return 0, 0

        space_width = stringWidth(' ', self.style.font_name, self.style.font_size)
        for word in self.words:

            if word is Break:
                line = [Break]
                lines.append(line)
                widths.append(0)
                continue

            word_width = word.width
            if widths[-1]+word_width > available_width:
                if line:
                    line = []
                    lines.append(line)
                    widths.append(0)

            widths[-1] += word_width + space_width
            line.append(word)

        self.height = len(lines) * self.style.leading
        return available_width, self.height

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
