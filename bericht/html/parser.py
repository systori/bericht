from io import BytesIO
from string import whitespace

from lxml import etree

from bericht.style import Style
from bericht.text import Paragraph, Word, Break
from bericht.table import Table, Row, Cell, Span

__all__ = ('parse_html',)


def parse_html(html, style=None):
    root = RootCollector(style or Style.default())
    stack = [root]
    context = etree.iterparse(
        BytesIO(html.encode('utf8')),
        events=('start', 'end',),
        tag=('table', 'tr', 'th', 'td', 'p'),
        html=True, remove_comments=True
    )
    for event, element in context:
        if event == 'start':
            # print("%5s, %4s" % (event, element.tag))
            stack.append(stack[-1].start(element))
        else:  # event == 'end':
            # print("%5s, %4s: '%s' '%s'" % (event, element.tag, element.text, element.tail))
            stack[-1].end(element)
            stack.pop()
            if element.tag in ('table', 'p'):
                # clear() can be expensive, don't bother calling it for the small things
                element.clear()
    return stack[0].flowables


NESTING_ERROR = "'{}' not allowed inside of '{}', maybe a missing close tag?"


class Collector:

    tag = None
    children = {}

    def __init__(self, style):
        self.style = style
        self.flowables = []

    def start(self, e):
        assert e.tag in self.children, NESTING_ERROR.format(e.tag, self.tag)
        collector = self.children[e.tag](self.style)
        self.flowables.append(collector.flowable)
        return collector

    def end(self, e):
        assert e.tag == self.tag
        return True


class ParagraphCollector(Collector):

    tag = 'p'

    def __init__(self, style):
        super().__init__(style)
        self.styles = [style]
        self.words = []
        self.word_open = False
        self.flowable = Paragraph(self.words, style)

    def start(self, element):
        # paragraph has no inner structures other than styling tags
        raise RuntimeError

    def end(self, paragraph):
        if paragraph.text:
            self.data(paragraph.text)
        context = etree.iterwalk(
            paragraph, events=('start', 'end'),
            tag=('b', 'strong', 'i', 'u', 'span', 'br')
        )
        for event, element in context:
            tag = element.tag
            if event == 'start':
                if tag in ('b', 'strong'):
                    self.styles.append(self.styles[-1].set(bold=True))
                elif tag == 'i':
                    self.styles.append(self.styles[-1].set(italic=True))
                elif tag == 'u':
                    self.styles.append(self.styles[-1].set(underline=True))
                if element.text:
                    self.data(element.text)
            else:  # event == 'end':
                if tag == 'br':
                    self.words.append(Break)
                else:
                    self.styles.pop()
                if element.tail:
                    self.data(element.tail)

    def data(self, data):
        if data[0] in whitespace or (self.words and self.words[-1] is Break):
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
        self.flowable = Table([], self.flowables, style)

CellCollector.children['table'] = TableCollector


class RootCollector(Collector):
    children = {
        'p': ParagraphCollector,
        'table': TableCollector
    }
