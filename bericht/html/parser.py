from string import whitespace
from lxml.etree import HTMLPullParser
from bericht.node import Style
from bericht.node import Paragraph, Word, Break
from bericht.node import Table, Row, Cell
from bericht.node import ColumnGroup, Column, RowGroup

__all__ = ('HTMLParser',)


def pumper(source, pump, stream):
    while True:
        for chunk in stream:
            yield chunk
        try:
            pump(next(source))
        except StopIteration:
            break


TAG_MAP = {
    'p': Paragraph,
    'table': Table,
    'colgroup': ColumnGroup,
    'col': Column,
    'thead': RowGroup,
    'tbody': RowGroup,
    'tfoot': RowGroup,
    'tr': Row,
    'td': Cell,
}

STYLE_TAGS = 'b', 'strong', 'i', 'u', 'span', 'br'


class HTMLParser:

    def __init__(self, html_generator):
        parser = HTMLPullParser(
            events=('start', 'end',),
            tag=tuple(TAG_MAP.keys()) + STYLE_TAGS,
            remove_comments=True
        )
        self.events = pumper(
            html_generator,
            parser.feed,
            parser.read_events()
        )

    def traverse(self, parent=None):
        for event, element in self.events:
            tag = element.tag

            if event == 'start':

                if tag in STYLE_TAGS:
                    node = parent
                    if tag in ('b', 'strong'):
                        node.styles.append(node.styles[-1].set(bold=True))
                    elif tag == 'i':
                        node.styles.append(node.styles[-1].set(italic=True))
                    elif tag == 'u':
                        node.styles.append(node.styles[-1].set(underline=True))
                    if element.text:
                        self.data(node, element.text)
                else:
                    if tag == 'tr' and isinstance(parent, Table):
                        parent = parent.get_tbody()
                    node = TAG_MAP[tag](
                        tag, parent,
                        element.attrib.get('id', None),
                        element.attrib.get('class', None),
                        Style.default()
                    )
                    if tag == 'col':
                        node.width = element.attrib.get('width', '')

                if isinstance(node, Table):
                    for row in self.traverse(node):
                        if row.parent.tag == 'tbody':
                            yield row
                else:
                    for _ in self.traverse(node):
                        pass
                    yield node

            else:
                if tag == 'p':
                    if element.text:
                        self.data(parent, element.text)
                if parent.tag == 'p':
                    if tag == 'br':
                        parent.words.append(Break)
                    else:
                        parent.styles.pop()
                    if element.tail:
                        self.data(parent, element.tail)
                break

    def data(self, node, data):
        if data[0] in whitespace or (node.words and node.words[-1] is Break):
            node.word_open = False
        parts = data.split()
        if not parts:
            return
        word_iter = iter(parts)
        style = node.styles[-1]
        if node.word_open:
            node.words[-1].add(style, next(word_iter))
        node.words.extend(Word(style, word) for word in word_iter)
        node.word_open = data[-1] not in whitespace

    def __iter__(self):
        yield from self.traverse()
