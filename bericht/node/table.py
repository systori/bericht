from .block import Block
from .style import Style, BorderCollapse
from .text import Paragraph


__all__ = ['Table', 'ColumnGroup', 'Column', 'RowGroup']


class ColumnGroup:

    def __init__(self, tag, parent, id=None, classes=None, css=None, position=None):
        self.tag = tag
        self.parent = parent
        self.id = id
        self.classes = classes or []
        self.css = css
        self.position = position
        self.children = []
        self.widths = None
        self.measurements = None
        self.span = None
        parent.columns = self

    def add(self, child):
        self.children.append(child)

    @property
    def count(self):
        if self.span is not None:
            return self.span
        return len(self.children)

    def get_widths(self, available_width):
        if self.widths is None:
            if self.span is None:
                self.calculate_widths(available_width)
            else:
                self.widths = [available_width/self.span] * self.span
        return self.widths

    def calculate_widths(self, available_width):

        widths = self.measurements[:]

        fixed = sum(widths)

        units = 0
        for c in self.children:
            if c.is_proportional:
                units += c.proportion

        unit_size = (available_width - fixed) / units
        for i in range(len(self.children)):
            c = self.children[i]
            if c.is_proportional:
                widths[i] = c.proportion * unit_size

        self.widths = widths

    def measure(self, row, maximums):
        if not self.children: return
        cols = iter(self.children)
        icol = 0
        for cell in row.children:
            if not cell or cell.colspan == 1:
                col = next(cols)
                if cell and cell.children:
                    assert isinstance(cell.children[0], Paragraph)
                    cell.css.apply(cell)
                    maximums[icol] = max(maximums[icol], col.measure(cell.children[0]))
                icol += 1
            else:
                # multi-column spans aren't measured
                for _ in range(cell.colspan):
                    next(cols)
                    icol += 1


class Column:

    def __init__(self, tag, parent, id=None, classes=None, css=None, position=None):
        self.tag = tag
        self.parent = parent
        self.id = id
        self.classes = classes or []
        self.css = css
        self.position = position
        self.style = Style.default()
        self.children = []
        self.width_spec = ''
        self.parent.add(self)

    @property
    def is_fixed(self):
        return all(n in '0123456789' for n in self.width_spec)

    @property
    def fixed(self):
        return int(self.width_spec)

    @property
    def is_max_content(self):
        return self.width_spec in ('0*', 'max-content')

    @property
    def is_min_content(self):
        return self.width_spec in ('min-content',)

    @property
    def is_proportional(self):
        return self.width_spec.endswith('*') and self.width_spec != '0*'

    @property
    def proportion(self):
        return int(self.width_spec[:-1])

    def measure(self, row):
        if self.is_fixed:
            return self.fixed
        elif self.is_max_content:
            return row.wrap(None, 1000)[0]
        elif self.is_min_content:
            return row.wrap(None, 0)[0]
        return 0


class RowGroup:

    def __init__(self, tag, parent, id=None, classes=None, css=None, position=None):
        self.tag = tag
        self.parent = parent
        self.id = id
        self.classes = classes or []
        self.css = css
        self.position = 1
        self.style = Style.default()
        self.children = []
        self.drawn_on = None
        setattr(parent, tag, self)

    def add(self, child):
        self.children.append(child)

    def wrap(self, page, available_width):
        header_height = 0
        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)
        for row in self.children:
            header_height += row._wrap(page, available_width)[1]
        return header_height

    def draw(self, page, x, y):
        self.drawn_on = page.page_number
        for row in self.children:
            x, y = row._draw(page, x, y)
        self.position += 1
        return x, y


class Table(Block):

    __slots__ = ('columns', 'thead', 'tbody', 'tfoot', 'buffered', 'row_heights')

    def __init__(self, *args):
        super().__init__(*args)
        self.columns = None
        self.thead = None
        self.tbody = None
        self.tfoot = None
        self.buffered = False
        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)

    def add(self, child):
        if self.buffered:
            super().add(child)

    @classmethod
    def make(cls, parent=None, id=None, classes=None, style=None):
        return cls('table', parent, id, classes, style)

    def get_tbody(self):
        if not self.tbody:
            self.tbody = RowGroup('tbody', self, css=self.css)
        return self.tbody

    def get_columns(self):
        if self.columns is None:
            self.columns = ColumnGroup('colgroup', self)
        return self.columns

    def get_column_widths(self, available_width):
        return self.get_columns().get_widths(available_width)

    def reserve_header_height(self, page, available_width):
        if self.thead and self.thead.drawn_on != page.page_number:
            return self.thead.wrap(page, available_width)
        return 0

    def reserve_footer_height(self, page, available_width):
        if self.tfoot:
            return self.tfoot.wrap(page, available_width)
        return 0

    def wrap(self, page, available_width):
        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)
        self.height = (
            self.reserve_header_height(page, available_width) +
            self.tbody.wrap(page, available_width) +
            self.reserve_header_height(page, available_width)
        )
        self.width = available_width
        return self.width, self.height

    def draw_header(self, page, x, y):
        if self.thead and self.thead.drawn_on != page.page_number:
            return self.thead.draw(page, x, y)
        return x, y

    def draw_footer(self, page, x, y):
        if self.tfoot:
            return self.tfoot.draw(page, x, y)
        return x, y

    def draw(self, page, x, y):
        x, y = self.draw_header(page, x, y)
        x, y = self.tbody.draw(page, x, y)
        x, y = self.draw_footer(page, x, y)
        return x, y

    def old_wrap(self, available_width, _=None):
        collapsed = self.style.border_collapse == BorderCollapse.collapse
        columns_available_width = available_width - self.frame_width
        vspacing = hspacing = 0
        if not collapsed:
            vspacing = self.style.border_spacing_vertical
            hspacing = self.style.border_spacing_horizontal
            columns_available_width -= hspacing*len(self.columns)
        self.calculate_ratio_columns(columns_available_width)
        self.width = available_width
        self.height = self.frame_height
        self.content_heights = []
        for row in self.rows:
            row.collapsed = collapsed
            row.cell_spacing = hspacing
            _, height = row.wrap(self.content_widths)
            height += vspacing
            self.content_heights.append(height)
            self.height += height
        return available_width, self.height

    def old_split(self, available_width, available_height):
        if self.content_heights is None:
            self.wrap(available_width)

        assert self.content_heights, "Split called on empty table."

        if self.tfoot:

            # check that footer fits, exit fast if not
            footer_height = sum(self.content_heights[-len(self.tfoot):])
            if footer_height >= available_height:
                return []

            # reduce the available height by footer to make sure there is always room for it
            available_height -= footer_height

        heights = iter(self.content_heights)

        # now check if header also fits, exit fast if not
        header_height = 0
        for _, height in zip(self.thead, heights):
            header_height += height
            if header_height >= available_height:
                return []

        # finally lets see if some rows fit sandwiched between thead/tfoot
        split_at_row = -1
        split_row_height = 0
        consumed_height = header_height
        for split_at_row, (row, split_row_height) in enumerate(zip(self.content, heights)):
            consumed_height += split_row_height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.content) == 1 or len(self.content)-1 == split_at_row:
                # nothing to split
                return [self]
            else:
                # table split cleanly between rows, no need to further split any rows/cells
                return [
                    Table(self.ratios, self.columns, self.content[:split_at_row+1], self.style, self.thead, self.tfoot, was_split=True),
                    Table(self.ratios, self.columns, self.content[split_at_row-1:], self.style, self.thead, self.tfoot, was_split=True)
                ]

        top_rows = self.content[:split_at_row]
        row = self.content[split_at_row]
        bottom_rows = self.content[split_at_row+1:]

        top_height = available_height - (consumed_height - split_row_height)
        if self.style.border_collapse == BorderCollapse.separate:
            top_height -= self.style.border_spacing_vertical
        split = row.splitOn(None, available_width, top_height)

        if not split:
            # cell could not be split,
            # move entirely to bottom half
            bottom_rows.insert(0, row)
        elif len(split) == 1:
            # cell completely fits in top half,
            # add placeholder to bottom half
            top_rows.append(row)
        elif len(split) == 2:
            top_rows.append(split[0])
            bottom_rows.insert(0, split[1])
        else:
            raise LayoutError("Splitting row {} produced unexpected result.".format(split_at_row))

        return [] if not top_rows else [
            Table(self.ratios, self.columns, top_rows, self.style, self.thead, self.tfoot, was_split=True),
            Table(self.ratios, self.columns, bottom_rows, self.style, self.thead, self.tfoot, was_split=True)
        ]
