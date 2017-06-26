from string import whitespace
from lxml.etree import HTMLPullParser
from bericht.node import Style
from bericht.node import Paragraph, Word, Break
from bericht.node import Table, Row, Cell, Span

__all__ = ('HTMLParser',)


def pumper(source, pump, stream):
    while True:
        for chunk in stream:
            yield chunk
        try:
            pump(next(source))
        except StopIteration:
            break


class HTMLParser:

    STYLE_TAGS = 'b', 'strong', 'i', 'u', 'span', 'br'

    def __init__(self, html_generator):
        parser = HTMLPullParser(
            events=('start', 'end',),
            tag=('table', 'tr', 'th', 'td', 'p') + HTMLParser.STYLE_TAGS,
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

                node = None
                if tag in HTMLParser.STYLE_TAGS:
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
                    if tag == 'p':
                        node = Paragraph([], Style.default())
                    elif tag == 'table':
                        node = Table()
                    elif tag == 'tr':
                        node = Row()

                    if parent:
                        parent.children.append(node)
                        node.parent = parent

                if isinstance(node, Table):
                    for row in self.traverse(node):
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
