from enum import Enum
from collections import namedtuple

from reportlab.lib.fonts import tt2ps
from reportlab.lib.colors import black

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
    namedtuple('_TextStyle', ('font', 'font_size', 'bold', 'italic', 'underline')), TextProps):

    @classmethod
    def from_style(cls, block):
        return cls(*block[:TEXT_PROP_COUNT]).set()

    def validate(self, **kwargs):
        for key, value in kwargs.items():
            if key in ('font',):
                assert isinstance(value, str), "{} is not a str: {}".format(key, value)
            if key in ('font_size',):
                assert isinstance(value, int), "{} is not an int: {}".format(key, value)
            if key in ('bold', 'italic', 'underline'):
                assert isinstance(value, bool), "{} is not a bool: {}".format(key, value)


TEXT_PROP_COUNT = len(TextStyle._fields)


class BlockProps(TextProps):
    pass


class BorderStyle(Enum):
    solid = 1
    dashed = 2


@cache_styles
class BlockStyle(
        namedtuple(
        '_BlockStyle',
        TextStyle._fields + (
            'align',
            'border_top_color',
            'border_top_style',
            'border_top_width',
            'border_right_color',
            'border_right_style',
            'border_right_width',
            'border_bottom_color',
            'border_bottom_style',
            'border_bottom_width',
            'border_left_color',
            'border_left_style',
            'border_left_width',
        )), BlockProps):

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
            underline=False,
            align=Align.left,
            border_top_color=black,
            border_top_style=BorderStyle.solid,
            border_top_width=0,
            border_right_color=black,
            border_right_style=BorderStyle.solid,
            border_right_width=0,
            border_bottom_color=black,
            border_bottom_style=BorderStyle.solid,
            border_bottom_width=0,
            border_left_color=black,
            border_left_style=BorderStyle.solid,
            border_left_width=0,
        )

    def validate(self, **kwargs):
        TextStyle.validate(self, **kwargs)
        for key, value in kwargs.items():
            if key == 'align':
                assert isinstance(value, Align)


BLOCK_PROP_COUNT = len(BlockStyle._fields)


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
