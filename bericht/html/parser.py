from lxml import etree

from bericht.style import BlockStyle
from bericht.text import Paragraph, Word
from bericht.table import Table, Row, Cell

__all__ = ['parse_html']


def parse_html(html, style):
    target = ParserEventTarget(style or BlockStyle.default())
    parser = etree.HTMLParser(
        remove_comments=True,
        target=target
    )
    return etree.HTML(html, parser)


class Collector:

    tag = None
    children = {}

    def __init__(self, style):
        self.style = style
        self.flowables = []

    def start(self, tag, attrib):
        assert tag in self.children
        collector = self.children[tag](self.style)
        self.flowables.append(collector.flowable)
        return collector

    def end(self, tag):
        assert tag == self.tag
        return True

    def data(self, data):
        pass


class ParagraphCollector(Collector):

    tag = 'p'
    allowed = ('b', 'i', 'u', 'span')

    def __init__(self, style):
        super().__init__(style)
        self.styles = [style]
        self.words = []
        self.flowable = Paragraph(self.words, style)

    def start(self, tag, attrib):
        assert tag in self.allowed
        getattr(self, 'start_'+tag)(attrib)

    def start_b(self, attrib):
        self.styles.append(self.styles[-1].set(bold=True))

    def start_i(self, attrib):
        self.styles.append(self.styles[-1].set(italic=True))

    def end(self, tag):
        if tag == 'p':
            return True
        else:
            self.styles.pop()

    def data(self, data):
        style = self.styles[-1]
        self.words.extend(Word(style, word) for word in data.split())


class CellCollector(Collector):
    tag = 'td'
    children = {
        'p': ParagraphCollector
    }

    def __init__(self, style):
        super().__init__(style)
        self.flowable = Cell(self.flowables, style)


class RowCollector(Collector):
    tag = 'tr'
    children = {
        'td': CellCollector,
    }

    def __init__(self, style):
        super().__init__(style)
        self.flowable = Row(self.flowables, style)


class TableCollector(Collector):
    tag = 'table'
    children = {
        'tr': RowCollector,
    }

    def __init__(self, style):
        super().__init__(style)
        self.flowable = Table(self.flowables, style)

CellCollector.children['table'] = TableCollector


class RootCollector(Collector):

    children = {
        'p': ParagraphCollector,
        'table': TableCollector
    }

    def end(self, tag):
        # RootCollector should never end.
        raise AssertionError('Extraneous end tag: '+tag)


class ParserEventTarget:

    def __init__(self, style):
        assert isinstance(style, BlockStyle)
        self.stack = [RootCollector(style)]
        self.tag_stack = []

    def start(self, tag, attrib):
        self.tag_stack.append(tag)
        if tag not in ('html', 'body'):
            collector = self.stack[-1].start(tag, attrib)
            if collector:
                self.stack.append(collector)

    def end(self, tag):
        start = self.tag_stack.pop()
        assert start == tag, 'End tag ({}) does not match start tag ({}).'.format(tag, start)
        if tag not in ('html', 'body'):
            if self.stack[-1].end(tag):
                self.stack.pop()

    def data(self, data):
        self.stack[-1].data(data)

    def close(self):
        assert len(self.tag_stack) == 0
        assert len(self.stack) == 1
        return self.stack[0].flowables
