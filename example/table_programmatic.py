from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, green, blue, red

from bericht.style import *
from bericht.table import *
from bericht.text import *


S = Style.default().set(
    border_top_width=3,
    border_top_color=green,
    border_right_width=2,
    border_right_color=blue,
    border_bottom_width=1,
    border_bottom_color=red,
    border_left_width=1,
    margin_top=3,
    margin_left=3,
    margin_bottom=3,
    margin_right=3,
)

doc = SimpleDocTemplate('example.pdf', pagesize=letter)

tables = []

builder = TableBuilder([1, 1, 1], S)
builder.row(
    para("Top Left "*10),
    para("Top Center", S.set(text_align=TextAlign.center)),
    para("Top Right", S.set(text_align=TextAlign.right))
)
builder.row(
    para("Left."), Span.col, Span.col
)
builder.row(
    para("Middle Left "*10),
    para("Middle Center", S.set(text_align=TextAlign.center)),
    para("Middle Right", S.set(text_align=TextAlign.right)),
    cell_style=S.set(vertical_align=VerticalAlign.middle)
)
builder.row(
    para("Center.", S.set(text_align=TextAlign.center)), Span.col, Span.col
)
builder.row(
    para("Bottom Left "*10),
    para("Bottom Center", S.set(text_align=TextAlign.center)),
    para("Bottom Right", S.set(text_align=TextAlign.right)),
    cell_style=S.set(vertical_align=VerticalAlign.bottom)
)
builder.row(
    para("Right.", S.set(text_align=TextAlign.right)), Span.col, Span.col
)
tables.append(builder.table)


S = Style.default().set(
    border_top_width=1,
    border_bottom_width=1,
    border_right_width=1,
    border_left_width=1,
    border_top_color=black,
    border_right_color=black,
    border_bottom_color=black,
    border_left_color=black,
    text_align=TextAlign.right,
    vertical_align=VerticalAlign.top,
    border_collapse=BorderCollapse.collapse,
)

builder = TableBuilder([1]*11, S)
for i in range(11):
    builder.row(*(i*j for j in range(11)))
builder.row(*(
    [static("center", S.set(text_align=TextAlign.center))] +
    [Span.col for i in range(10)]
))
tables.append(builder.table)

doc.build(tables)
