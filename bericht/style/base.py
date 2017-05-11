from enum import Enum
from collections import namedtuple

from reportlab.lib.fonts import tt2ps

from .utils import cache_styles


__all__ = (
    'Align', 'VerticalAlign', 'Span',
    'BlockStyle', 'TextStyle',
    'TableStyle', 'RowStyle', 'CellStyle',
)


class Align(Enum):
    left = 1
    center = 2
    right = 3
    justify = 4


class TextProps:

    @property
    def font_name(self):
        return tt2ps(self.font, self.bold, self.italic)

    @property
    def leading(self):
        return int(self.font_size * 1.2)


@cache_styles
class TextStyle(
    namedtuple('_TextStyle', ('font', 'font_size', 'bold', 'italic')), TextProps):

    @classmethod
    def from_style(cls, block):
        return cls(*block[:4]).set()

    def validate(self, **kwargs):
        for key, value in kwargs.items():
            if key in ('bold', 'italic'):
                assert isinstance(value, bool)


class BlockProps(TextProps):
    pass


BLOCK_PROP_COUNT = len(TextStyle._fields) + 1


@cache_styles
class BlockStyle(
    namedtuple('_BlockStyle', TextStyle._fields + ('align',)), BlockProps):

    @classmethod
    def from_style(cls, block):
        return cls(*block[:BLOCK_PROP_COUNT]).set()

    @classmethod
    def default(cls):
        return cls(
            font='Helvetica',
            font_size=12,
            bold=False,
            italic=False,
            align=Align.left
        )

    def validate(self, **kwargs):
        TextStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            if key == 'align':
                assert isinstance(value, Align)


class VerticalAlign(Enum):
    top = 1
    middle = 2
    bottom = 3


class Span(Enum):
    col = 1
    row = 2


@cache_styles
class CellStyle(
    namedtuple('_CellStyle', BlockStyle._fields + ('vertical_align',)), BlockProps):

    @classmethod
    def from_style(cls, block):
        return cls(*block[:BLOCK_PROP_COUNT], VerticalAlign.top).set()

    def validate(self, **kwargs):
        BlockStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            if key == 'vertical_align':
                assert isinstance(value, VerticalAlign)


@cache_styles
class RowStyle(
    namedtuple('_RowStyle', BlockStyle._fields + ('page_break_inside',)), BlockProps):

    @classmethod
    def from_style(cls, block):
        return cls(*block[:BLOCK_PROP_COUNT], True).set()

    def validate(self, **kwargs):
        BlockStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            if key == 'page_break_inside':
                assert isinstance(value, bool)


@cache_styles
class TableStyle(
    namedtuple('_TableStyle', BlockStyle._fields), BlockProps):

    @classmethod
    def from_style(cls, block):
        return cls(*block[:BLOCK_PROP_COUNT]).set()

    def validate(self, **kwargs):
        BlockStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            pass
