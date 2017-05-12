from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import green, blue, red

from bericht.style import *
from bericht.table import *


S = Style.default()

doc = SimpleDocTemplate('example.pdf', pagesize=letter)
builder = TableBuilder(S.set(
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
))
builder.row("Top Left", "Top", "Top Right")
builder.row("Middle Left", "Middle Center", "Middle Right")
builder.row("Bottom Left", "Bottom Center", "Bottom Right")
builder.row("Span three cols.", Span.col, Span.col)
doc.build([builder.table])
