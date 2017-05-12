from string import whitespace

from lxml import etree

from bericht.style import Style
from bericht.text import Paragraph, Word, Break
from bericht.table import Table, Row, Cell, Span

__all__ = ('parse_html',)


def parse_html(html, style=None):
    target = ParserEventTarget(style or Style.default())
    parser = etree.XMLParser(
        remove_comments=True,
        target=target
    )
    return etree.XML(''.join(('<root>', html, '</root>')), parser)


NESTING_ERROR = "'{}' not allowed inside of '{}', maybe a missing close tag?"


class Collector:

    tag = None
    children = {}

    def __init__(self, style):
        self.style = style
        self.flowables = []

    def start(self, tag, attrib):
        assert tag in self.children, NESTING_ERROR.format(tag, self.tag)
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
    allowed = ('b', 'strong', 'i', 'u', 'span', 'br')

    def __init__(self, style):
        super().__init__(style)
        self.styles = [style]
        self.words = []
        self.word_open = False
        self.flowable = Paragraph(self.words, style)

    def start(self, tag, attrib):
        assert tag in self.allowed, NESTING_ERROR.format(tag, self.tag)
        getattr(self, 'start_'+tag)(attrib)

    def start_b(self, attrib):
        self.styles.append(self.styles[-1].set(bold=True))
    start_strong = start_b

    def start_i(self, attrib):
        self.styles.append(self.styles[-1].set(italic=True))

    def start_u(self, attrib):
        self.styles.append(self.styles[-1].set(underline=True))

    def start_br(self, attrib):
        self.words.append(Break)

    def end(self, tag):
        if tag == 'p':
            return True
        elif tag == 'br':
            pass
        else:
            self.styles.pop()

    def data(self, data):
        if data[0] in whitespace:
            self.word_open = False
        parts = data.split()
        if not parts:
            return
        word_iter = iter(parts)
        style = self.styles[-1]
        if self.word_open:
            self.words[-1].add(style, next(word_iter))
        self.words.extend(Word(style, word) for word in word_iter)
        self.word_open = data[-1] not in whitespace


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
        return False


class ParserEventTarget:

    def __init__(self, style):
        self.root = RootCollector(style)
        self.stack = []
        self.tag_stack = []

    def start(self, tag, attrib):
        self.tag_stack.append(tag)
        if tag == 'root':
            assert not self.stack
            collector = self.root
        else:
            collector = self.stack[-1].start(tag, attrib)
        if collector:
            self.stack.append(collector)

    def end(self, tag):
        start = self.tag_stack.pop()
        assert start == tag, 'End tag ({}) does not match start tag ({}).'.format(tag, start)
        if self.stack[-1].end(tag):
            self.stack.pop()

    def data(self, data):
        self.stack[-1].data(data)

    def close(self):
        assert len(self.tag_stack) == 0, 'Unclosed tags: {}'.format(self.tag_stack)
        assert len(self.stack) == 1
        return self.stack[0].flowables
