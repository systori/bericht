bericht
=======

Improved tabular report generation with ReportLab.

to test things real quick:

``` python
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from bericht import TableBuilder, Span

rlstyle = getSampleStyleSheet()['BodyText']

builder = TableBuilder(rlstyle)

builder.row('this is a test1', 'second cell1', 'ending cell1')
builder.row('this is a test', 'second cell', 'ending cell', 'forth cell')
builder.row('this is a test', Span.COL, 'forth cell')

doc = SimpleDocTemplate('test.pdf', pagesize=A4)
doc.build([builder.table])
```

