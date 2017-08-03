from enum import Enum
from collections import namedtuple

from reportlab.lib.fonts import tt2ps
from reportlab.lib.colors import Color, black


__all__ = (
    'Style', 'TextAlign', 'VerticalAlign',
    'BorderStyle', 'BorderCollapse',
)


class TextAlign:
    left = 'left'
    center = 'center'
    right = 'right'
    justify = 'justify'


class VerticalAlign:
    top = 'top'
    middle = 'middle'
    bottom = 'bottom'


class BorderStyle(Enum):
    solid = 1
    dashed = 2


class BorderCollapse(Enum):
    collapse = 1
    separate = 2


_style_cache = {}


class Style(namedtuple('_Style', (

        'set_attrs',

        'font', 'font_size', 'font_weight', 'font_style', 'text_decoration',

        'text_align', 'vertical_align',

        'padding_top', 'padding_right', 'padding_bottom', 'padding_left',

        'border_top_color', 'border_top_style', 'border_top_width',
        'border_left_color', 'border_left_style', 'border_left_width',
        'border_right_color', 'border_right_style', 'border_right_width',
        'border_bottom_color', 'border_bottom_style', 'border_bottom_width',

        'margin_top', 'margin_right', 'margin_bottom', 'margin_left',

        'background_color',

        'page_break_before',
        'page_break_inside',
        'page_break_after',

        'page_bottom_right_content',

        'border_collapse',
        'border_spacing_horizontal',
        'border_spacing_vertical',

        'letterhead_page'

        ))):

    @classmethod
    def default(cls):
        return cls(

            set_attrs=tuple(),

            font='OpenSans',
            font_size=12,
            font_weight='',
            font_style='',
            text_decoration='',

            text_align='left',

            vertical_align='top',

            padding_top=0,
            padding_right=0,
            padding_bottom=0,
            padding_left=0,

            border_top_color=(0, 0, 0, 1),
            border_top_style=BorderStyle.solid,
            border_top_width=0,
            border_right_color=(0, 0, 0, 1),
            border_right_style=BorderStyle.solid,
            border_right_width=0,
            border_bottom_color=(0, 0, 0, 1),
            border_bottom_style=BorderStyle.solid,
            border_bottom_width=0,
            border_left_color=(0, 0, 0, 1),
            border_left_style=BorderStyle.solid,
            border_left_width=0,

            margin_top=0,
            margin_right=0,
            margin_bottom=0,
            margin_left=0,

            background_color=None,

            page_break_before=False,
            page_break_inside=True,
            page_break_after=False,

            page_bottom_right_content='',

            border_collapse=BorderCollapse.separate,
            border_spacing_horizontal=2,
            border_spacing_vertical=2,

            letterhead_page=1
        )

    def set(self, **attrs):
        attrs = self.convert(attrs)
        _ts = self._replace(
            set_attrs=tuple(set(self.set_attrs) | set(attrs.keys())),
            **attrs,
        )
        ts = _style_cache.setdefault(hash(_ts), _ts)
        if ts is _ts:  # validate if we just added this new style to cache
            ts.validate(**attrs)
        return ts

    def inherit(self, other):
        return self.set(**{
            attr: getattr(other, attr) for attr in other.set_attrs if attr not in self.set_attrs
        })

    @staticmethod
    def convert(kwargs):
        if 'page_break_before' in kwargs:
            kwargs['page_break_before'] = kwargs['page_break_before'] == 'always'
        if 'page_break_after' in kwargs:
            kwargs['page_break_after'] = kwargs['page_break_after'] == 'always'
        return kwargs

    def validate(self, **kwargs):
        for key, value in kwargs.items():
            if key in ('font', 'font_weight', 'font_style', 'text_decoration', 'text_align', 'vertical_align'):
                assert isinstance(value, str)
            elif key in ('font_size', 'border_spacing'):
                assert isinstance(value, (int, float))
            elif key in ('page_break_inside',):
                assert isinstance(value, bool)
            elif key == 'border_collapse':
                assert isinstance(value, BorderCollapse)
            elif key.startswith('border'):
                _, _, field = key.split('_')
                if field == 'color':
                    assert isinstance(value, Color)
                elif field == 'style':
                    assert isinstance(value, BorderStyle)
                elif field == 'width':
                    assert isinstance(value, (int, float))
            elif key.startswith('padding') or key.startswith('margin'):
                assert isinstance(value, (int, float))

    @property
    def bold(self):
        return 1 if self.font_weight == 'bold' else 0

    @property
    def italic(self):
        return 1 if self.font_style == 'italic' else 0

    @property
    def font_name(self):
        return tt2ps(self.font, self.bold, self.italic)

    @property
    def leading(self):
        return int(self.font_size * 1.2)
