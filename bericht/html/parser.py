from string import whitespace
from lxml import etree
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
    'bericht-col': Column,
    'thead': RowGroup,
    'tbody': RowGroup,
    'tfoot': RowGroup,
    'tr': Row,
    'td': Cell,
}

BLOCK_TAGS = tuple(TAG_MAP.keys())
STYLE_TAGS = 'b', 'strong', 'i', 'u', 'span', 'br'


class HTMLParser:

    def __init__(self, html_generator, css=None):
        parser = etree.HTMLPullParser(
            events=('start', 'end',),
            tag=BLOCK_TAGS + STYLE_TAGS,
            remove_comments=True
        )
        self.events = pumper(
            html_generator,
            parser.feed,
            parser.read_events()
        )
        self.css = css

    def traverse(self, parent=None):
        for event, element in self.events:
            tag = element.tag

            assert tag in BLOCK_TAGS

            if event == 'start':

                if tag == 'tr' and isinstance(parent, Table):
                    parent = parent.get_tbody()

                node = TAG_MAP[tag](
                    tag, parent,
                    element.attrib.get('id', None),
                    element.attrib.get('class', None),
                    self.css,
                    1
                )

                if isinstance(node, Table):
                    if parent is None:
                        row_iter = self.traverse(node)
                        current_row = next(row_iter)
                        positions = {}
                        for next_row in row_iter:
                            positions.setdefault(current_row.parent.tag, -1)
                            positions[current_row.parent.tag] += 1
                            next_row.position = positions[current_row.parent.tag]
                            if current_row.parent.tag == 'tbody':
                                yield current_row
                            current_row = next_row
                        for cell in current_row.children:
                            if cell.children:
                                cell.children[-1].last_child = True
                        if current_row.children:
                            current_row.children[-1].last_child = True
                        current_row.last_child = True
                        yield current_row
                    else:
                        node.buffered = True
                        for _ in self.traverse(node):
                            pass
                        yield node

                elif isinstance(node, Paragraph):
                    self.fast_forward_to_end(element)
                    node.style = Style.default()
                    extract_words(node, element)
                    if isinstance(node, Column):
                        node.width_spec = element.attrib.get('width', '')
                    yield node

                else:

                    if isinstance(node, Cell):
                        node.colspan = int(element.attrib.get('colspan', 1))

                    elif isinstance(node, ColumnGroup):
                        span = element.attrib.get('span')
                        if span:
                            node.span = int(span)

                    for _ in self.traverse(node):
                        pass

                    yield node

            else:

                break

    def fast_forward_to_end(self, end):
        """ Fast forwarding (parsing) to end tag loads
            the element and its contents into memory.
            Sometimes it's necessary to have the entire
            element tree loaded to correctly process
            the contents (eg, <p></p> tags).
        """
        for event, element in self.events:
            if event == 'end' and element == end:
                return
        raise RuntimeError('End element not reached.')

    def __iter__(self):
        yield from self.traverse()


def extract_words(p, root):

    words = p.words
    styles = [p.style]
    word_open = False

    def data(data):
        nonlocal word_open
        if data[0] in whitespace or (words and words[-1] is Break):
            word_open = False
        parts = data.split()
        if not parts:
            return
        word_iter = iter(parts)
        style = styles[-1]
        if word_open:
            words[-1].add(p, style, next(word_iter))
        words.extend(Word(p, style, word) for word in word_iter)
        word_open = data[-1] not in whitespace

    if root.text:
        data(root.text)

    context = etree.iterwalk(
        root, events=('start', 'end'),
        tag=STYLE_TAGS
    )
    for event, element in context:
        tag = element.tag
        if event == 'start':
            if tag in ('b', 'strong'):
                styles.append(styles[-1].set(font_weight='bold'))
            elif tag == 'i':
                styles.append(styles[-1].set(font_style='italic'))
            elif tag == 'u':
                styles.append(styles[-1].set(text_decoration='underline'))
            if element.text:
                data(element.text)
        else:  # event == 'end':
            if tag == 'br':
                words.append(Break)
            else:
                styles.pop()
            if element.tail:
                data(element.tail)
