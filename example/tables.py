from bericht.html import HTMLParser, CSS
from bericht.pdf import PDFStreamer

css = CSS("""
.collapse {
  border-collapse: collapse;
}

.separate {
  border-collapse: separate;
}

table {
  margin: 5px;
  border-style: dashed;
  border-width: 5px;
}

table th,
table td {
  border-style: solid;
  border-width: 3px;
}

.fx { border-color: orange blue; }
.gk { border-color: black red; }
.ed { border-color: blue gold; }
.tr { border-color: aqua; }
.sa { border-color: silver blue; }
.wk { border-color: gold blue; }
.ch { border-color: red yellow green blue; }
.bk { border-color: navy blue teal aqua; }
.op { border-color: red; }
""")


def html():
    yield """
<!-- Learn about this code on MDN: https://developer.mozilla.org/en-US/docs/Web/CSS/border-collapse -->
<table class="separate">
  <caption><code>border-collapse: separate</code></caption>
  <tbody>
    <tr><th>Browser</th> <th>Layout Engine</th></tr>
    <tr><td class="fx">Firefox</td> <td class="gk">Gecko</td></tr>
    <tr><td class="ed">Edge</td> <td class="tr">EdgeHTML</td></tr>
    <tr><td class="sa">Safari</td> <td class="wk">Webkit</td></tr>
    <tr><td class="ch">Chrome</td> <td class="bk">Blink</td></tr>
    <tr><td class="op">Opera</td> <td class="bk">Blink</td></tr>
  </tbody>
</table>
<br>
<table class="collapse">
  <caption><code>border-collapse: collapse</code></caption>
  <tbody>
    <tr><th>Browser</th> <th>Layout Engine</th></tr>
    <tr><td class="fx">Firefox</td> <td class="gk">Gecko</td></tr>
    <tr><td class="ed">Edge</td> <td class="tr">EdgeHTML</td></tr>
    <tr><td class="sa">Safari</td> <td class="wk">Webkit</td></tr>
    <tr><td class="ch">Chrome</td> <td class="bk">Blink</td></tr>
    <tr><td class="op">Opera</td> <td class="bk">Blink</td></tr>
  </tbody>
</table>
"""


with open('example.pdf', 'wb') as output:
    for page in PDFStreamer(HTMLParser(html, css)):
        output.write(page)
