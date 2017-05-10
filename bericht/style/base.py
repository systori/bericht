from collections import namedtuple
from enum import Enum
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


@cache_styles
class TextStyle(namedtuple('_TextStyle', ('font', 'font_size', 'bold', 'italic'))):

    @classmethod
    def from_block(cls, block):
        return cls(*block[:len(cls._fields)]).set()

    def validate(self, **kwargs):
        for key, value in kwargs.items():
            if key in ('bold', 'italic'):
                assert isinstance(value, bool)

    @property
    def font_name(self):
        return self.font

    @property
    def leading(self):
        return int(self.font_size * 1.2)

@cache_styles
class BlockStyle(namedtuple('_BlockStyle', TextStyle._fields + ('align',))):

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
class CellStyle(namedtuple('_CellStyle', BlockStyle._fields + ('vertical_align',))):

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
        BlockStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            if key == 'vertical_align':
                assert isinstance(value, VAlign)


@cache_styles
class RowStyle(namedtuple('_RowStyle', BlockStyle._fields + ('page_break_inside',))):

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
        BlockStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            if key == 'page_break_inside':
                assert isinstance(value, bool)


@cache_styles
class TableStyle(namedtuple('_TableStyle', BlockStyle._fields)):

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
        BlockStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            pass
