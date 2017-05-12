from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import green, blue, red

from bericht.style import *
from bericht.table import *


block_style = BlockStyle.default()
table_style = TableStyle.from_style(block_style)

doc = SimpleDocTemplate('example.pdf', pagesize=letter)
builder = TableBuilder(table_style.set(
    border_top_width=1,
    border_top_color=green,
    border_right_width=1,
    border_right_color=blue,
    border_bottom_width=1,
    border_bottom_color=red,
    border_left_width=1
))
builder.row("Top Left", "Top", "Top Right")
builder.row("Middle Left", "Middle Center", "Middle Right")
builder.row("Bottom Left", "Bottom Center", "Bottom Right")
builder.row("Span three cols.", Span.col, Span.col)
doc.build([builder.table])
