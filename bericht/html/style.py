from enum import Enum
from collections import namedtuple

from reportlab.lib.fonts import tt2ps
from reportlab.lib.colors import Color, black


__all__ = (
    'Style', 'TextAlign', 'VerticalAlign',
    'BorderStyle', 'BorderCollapse', 'default'
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


class Style(namedtuple('_Style', (

        'display', 'visibility',

        'font_family', 'font_size', 'font_weight', 'font_style', 'text_decoration', 'color',

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

    def set(self, **attrs):
        return self._replace(**self.clean(attrs))

    def inherit(self):
        return default.set(
            font_family=self.font_family,
            font_size=self.font_size,
            font_weight=self.font_weight,
            font_style=self.font_style,
            text_decoration=self.text_decoration,
            text_align=self.text_align,
            color=self.color,
            # TODO: add all inheritable attributes
        )

    @staticmethod
    def clean(kwargs):
        if 'page_break_before' in kwargs:
            kwargs['page_break_before'] = kwargs['page_break_before'] == 'always'
        if 'page_break_after' in kwargs:
            kwargs['page_break_after'] = kwargs['page_break_after'] == 'always'
        return kwargs

    @property
    def bold(self):
        return 1 if self.font_weight == 'bold' else 0

    @property
    def italic(self):
        return 1 if self.font_style == 'italic' else 0

    @property
    def font_name(self):
        return tt2ps(self.font_family, self.bold, self.italic)

    @property
    def leading(self):
        return int(self.font_size * 1.2)


default = Style(

    display=None,
    visibility=True,

    font_family='Helvetica',
    font_size=12,
    font_weight='',
    font_style='',
    text_decoration='',
    color=(0, 0, 0, 1),

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

    # TODO: add all CSS attributes
)
