from enum import Enum
from collections import namedtuple

from reportlab.lib.fonts import tt2ps
from reportlab.lib.colors import Color, black


__all__ = (
    'Style', 'TextAlign', 'VerticalAlign',
    'BorderStyle', 'BorderCollapse',
)


class TextAlign(Enum):
    left = 1
    center = 2
    right = 3
    justify = 4


class VerticalAlign(Enum):
    top = 1
    middle = 2
    bottom = 3


class BorderStyle(Enum):
    solid = 1
    dashed = 2


class BorderCollapse(Enum):
    collapse = 1
    separate = 2


_style_cache = {}


class Style(namedtuple('_Style', (

        'font', 'font_size', 'bold', 'italic', 'underline',

        'text_align', 'vertical_align',

        'padding_top', 'padding_right', 'padding_bottom', 'padding_left',

        'border_top_color', 'border_top_style', 'border_top_width',
        'border_left_color', 'border_left_style', 'border_left_width',
        'border_right_color', 'border_right_style', 'border_right_width',
        'border_bottom_color', 'border_bottom_style', 'border_bottom_width',

        'margin_top', 'margin_right', 'margin_bottom', 'margin_left',

        'page_break_inside',

        'border_collapse',
        'border_spacing_horizontal',
        'border_spacing_vertical',

        ))):

    @classmethod
    def default(cls):
        return cls(

            font='Helvetica',
            font_size=12,
            bold=False,
            italic=False,
            underline=False,

            text_align=TextAlign.left,

            vertical_align=VerticalAlign.top,

            padding_top=0,
            padding_right=0,
            padding_bottom=0,
            padding_left=0,

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

            margin_top=0,
            margin_right=0,
            margin_bottom=0,
            margin_left=0,

            page_break_inside=True,

            border_collapse=BorderCollapse.separate,
            border_spacing_horizontal=2,
            border_spacing_vertical=2,
        )

    def set(self, **attrs):
        _ts = self._replace(**attrs)
        ts = _style_cache.setdefault(hash(_ts), _ts)
        if ts is _ts:  # validate if we just added this new style to cache
            ts.validate(**attrs)
        return ts

    def validate(self, **kwargs):
        for key, value in kwargs.items():
            if key in ('font',):
                assert isinstance(value, str)
            elif key in ('font_size', 'border_spacing'):
                assert isinstance(value, int)
            elif key in ('bold', 'italic', 'underline', 'page_break_inside'):
                assert isinstance(value, bool)
            elif key == 'text_align':
                assert isinstance(value, TextAlign)
            elif key == 'vertical_align':
                assert isinstance(value, VerticalAlign)
            elif key == 'border_collapse':
                assert isinstance(value, BorderCollapse)
            elif key.startswith('border'):
                _, _, field = key.split('_')
                if field == 'color':
                    assert isinstance(value, Color)
                elif field == 'style':
                    assert isinstance(value, BorderStyle)
                elif field == 'width':
                    assert isinstance(value, int)
            elif key.startswith('padding') or key.startswith('margin'):
                assert isinstance(value, int)

    @property
    def font_name(self):
        return tt2ps(self.font, self.bold, self.italic)

    @property
    def leading(self):
        return int(self.font_size * 1.2)
