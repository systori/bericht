from itertools import chain
from lxml import etree
from .box import *
from .table import *

__all__ = ('HTMLParser',)


TAG_TO_DISPLAY = {
    'table': 'table',
    'colgroup': 'table-column-group',
    'col': 'table-column',
    'thead': 'table-header-group',
    'tfoot': 'table-footer-group',
    'tbody': 'table-row-group',
    'tr': 'table-row',
    'td': 'table-cell',
    'th': 'table-cell',

    'body': 'block',
    'div': 'block',
    'p': 'block',
    'br': 'block',
    'ul': 'block',
    'ol': 'block',

    'li': 'list-item',

    'span': 'inline',
    'a': 'inline',
    'b': 'inline',
    'strong': 'inline',
    'i': 'inline',
    'u': 'inline',
}


def pumper(html_generator):
    """
    Pulls HTML from source generator,
    feeds it to the parser and yields
    DOM elements.
    """
    source = html_generator()
    parser = etree.HTMLPullParser(
        events=('start', 'end',),
        remove_comments=True
    )
    while True:
        for element in parser.read_events():
            yield element
        try:
            parser.feed(next(source))
        except StopIteration:
            break


def iter_previous_current_last(child_iter):
    current_child = next(child_iter, None)
    if current_child:
        previous_child = None
        for next_child in child_iter:
            yield previous_child, current_child, False
            previous_child = current_child
            current_child = next_child
        yield previous_child, current_child, True


class HTMLParser:

    def __init__(self, html_generator, css=None):
        self.html_generator = html_generator
        self.css = css
        self.table_columns = None
        self.stream = None

    def parse(self, parent, prepend=None, root_rows=False):
        """
        https://www.w3.org/TR/html5/syntax.html
        See: 8.2.5 Tree construction
        """

        if prepend is not None:
            stream = chain([('start', prepend)], self.stream)
        else:
            stream = self.stream

        for event, element in stream:

            tag = element.tag

            if event == 'start':

                if isinstance(parent.behavior, Table):

                    # these are not direct descendants of <table>, add missing parent

                    if tag in ('td', 'th', 'tr'):
                        tbody = parent.behavior.tbody or self.make_child(parent, 'tbody', {})
                        yield from self.parse(tbody, element, root_rows=root_rows)
                        return

                    elif tag == 'col':
                        columns = parent.behavior.columns or self.make_child(parent, 'colgroup', {})
                        self.parse(columns, element)
                        return

                elif isinstance(parent.behavior, TableRowGroup):

                    # these are not direct descendants of <tbody>, add missing parent

                    if tag in ('td', 'th'):
                        row = self.make_child(parent, 'tr', {})
                        self.parse(row, element)
                        if root_rows:
                            yield None, row
                        return

                node = self.make_child(parent, tag, element.attrib)

                if parent.tag == 'body' and isinstance(node.behavior, Table):
                    yield from self.parse(node, root_rows=True)

                else:

                    last_child = None
                    position = 0
                    position_of_type = {}

                    for previous, (child_element, child_node), last in iter_previous_current_last(self.parse(node)):
                        if previous is not None:
                            if previous[0].tail:
                                # insert text between previous node and current node
                                node.insert(len(node.children)-2, previous[0].tail)
                        position_of_type.setdefault(child_node.tag, 0)
                        child_node.position = position = position + 1
                        child_node.position_of_type = position_of_type[child_node.tag] = position_of_type[child_node.tag] + 1
                        child_node.last = last
                        last_child = child_element

                    if element.text:
                        node.insert(0, element.text)

                    if last_child is not None and last_child.tail:
                        node.add(last_child.tail)

                    yield element, node

            else:
                break

    def make_child(self, parent, tag, attrib):
        node = Box(parent, tag, attrib)
        self.css.apply(node)
        if node.style.display is None:
            display = TAG_TO_DISPLAY.get(tag, 'block')
            node.style = node.style.set(display=display)
        node.behavior = self.get_behavior(parent.behavior if parent else None, node)
        if parent:
            if parent.buffered:
                parent.add(node)
            elif tag == 'table':
                node.buffered = False
        return node

    @staticmethod
    def get_behavior(parent, node):

        display = node.style.display

        if display == 'block':
            return Block(node)

        elif display == 'inline':
            return Inline(node)

        elif display == 'table':
            return Table(node)

        elif parent:

            if isinstance(parent, Table):
                if display == 'table-column-group':
                    return TableColumnGroup(node)

                elif display in ('table-header-group', 'table-row-group', 'table-footer-group'):
                    return TableRowGroup(node)

            elif display == 'table-column' and isinstance(parent, TableColumnGroup):
                return TableColumn(node)

            elif display == 'table-row' and isinstance(parent, TableRowGroup):
                return TableRow(node)

            elif display == 'table-cell' and isinstance(parent, TableRow):
                return TableCell(node)

            elif display == 'list-item' and isinstance(parent, Block):
                return ListItem(node)

        return Block(node)

    def measure_column_widths(self):
        table_columns = []
        columns = None
        for box in self.boxes():
            if isinstance(box.behavior, TableRow):
                table = box.parent.parent
                if table.get_columns() is not columns:
                    columns = table.get_columns()
                    table_columns.append([0]*columns.count)
                    if table.thead:
                        for hrow in table.thead.children:
                            columns.measure(hrow, table_columns[-1])
                    if table.tfoot:
                        for frow in table.tfoot.children:
                            columns.measure(frow, table_columns[-1])
                columns.measure(node, table_columns[-1])
        return table_columns

    def boxes(self):
        self.stream = pumper(self.html_generator)
        next(self.stream)  # html
        _, body_element = next(self.stream)  # body
        node = self.make_child(None, body_element.tag, body_element.attrib)
        node.buffered = False
        return map(lambda n: n[1], self.parse(node))

    def __iter__(self):
        #if self.table_columns is None:
        #    self.table_columns = self.measure_column_widths()
        yield from self.boxes()
