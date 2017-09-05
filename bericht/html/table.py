from .style import BorderCollapse
from .box import Box, Behavior


__all__ = (
    'Table',
    'TableColumnGroup', 'TableColumn',
    'TableRowGroup', 'TableRow', 'TableCell'
)


TABLE_CHILDREN = {
    'table-column-group': 0,
    'table-header-group': 1,
    'table-row-group': 2,
    'table-footer-group': 3
}


class Table(Behavior):
    __slots__ = ()

    def __init__(self, box):
        super().__init__(box)
        columns = Box(self.box, 'colgroup', {})
        box.children = [columns, None, None, None]
        columns.style = columns.style.set(display='table-column-group')
        columns.behavior = TableColumnGroup(columns)

    @property
    def text_allowed(self):
        return False

    @property
    def columns(self):
        return self.box.children[TABLE_CHILDREN['table-column-group']]

    @property
    def thead(self):
        return self.box.children[TABLE_CHILDREN['table-header-group']]

    @property
    def tbody(self):
        return self.box.children[TABLE_CHILDREN['table-row-group']]

    @property
    def tfoot(self):
        return self.box.children[TABLE_CHILDREN['table-footer-group']]

    def add(self, child):
        i = TABLE_CHILDREN[child.style.display]
        if i != TABLE_CHILDREN['table-column-group']:
            assert self.box.children[i] is None
        if i == TABLE_CHILDREN['table-row-group']:
            child.buffered = self.box.parent.tag != 'body'
        else:
            child.style = child.style.set(visibility=False)
            if i == TABLE_CHILDREN['table-column-group']:
                child.behavior.measurements = self.columns.behavior.measurements
        self.box.children[i] = child

    def get_column_widths(self, available_width):
        return self.columns.behavior.get_widths(available_width)

    def reserve_header_height(self, page, available_width):
        if self.thead and self.thead.behavior.drawn_on != page.page_number:
            return self.thead.wrap(page, available_width)
        return 0

    def reserve_footer_height(self, page, available_width):
        if self.tfoot:
            return self.tfoot.wrap(page, available_width)
        return 0

    def wrap(self, page, available_width):
        self.height = (
            self.reserve_header_height(page, available_width) +
            self.tbody.wrap(page, available_width) +
            self.reserve_header_height(page, available_width)
        )
        self.width = available_width
        return self.width, self.height

    def draw_header(self, page, x, y):
        if self.thead and self.thead.behavior.drawn_on != page.page_number:
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

    def table_old_wrap(self, available_width, _=None):
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

    def table_old_split(self, available_width, available_height):
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


class TableColumnGroup(Behavior):
    __slots__ = ('widths', 'measurements', 'span')

    def __init__(self, box):
        super().__init__(box)
        self.span = int(box.attrs.get('span', 1))
        self.widths = None
        self.measurements = []

    @property
    def text_allowed(self):
        return False

    @property
    def count(self):
        if self.span is not None:
            return self.span
        return len(self.box.children)

    def get_widths(self, available_width):
        if self.widths is None:
            if self.measurements:
                self.calculate_widths(available_width)
            else:
                self.widths = [available_width/self.span] * self.span
        return self.widths

    def calculate_widths(self, available_width):

        widths = self.measurements.copy()

        fixed = sum(widths)

        units = 0
        for c in self.box.children:
            if c.behavior.is_proportional:
                units += c.behavior.proportion

        unit_size = (available_width - fixed) / units
        for i in range(len(self.box.children)):
            c = self.box.children[i]
            if c.behavior.is_proportional:
                widths[i] = c.behavior.proportion * unit_size

        self.widths = widths

    def measure(self, row, data):
        maximums = data['maximums']
        if not self.box.children:
            data['span'] = max(data['span'], len(row.children))
            return
        cols = iter(self.box.children)
        icol = 0
        for cell in row.children:
            if not cell or cell.behavior.colspan == 1:
                col = next(cols)
                if cell and cell.children:
                    width = col.behavior.measure(cell) + cell.frame_width
                    maximums[icol] = max(maximums[icol], width)
                icol += 1
            else:
                # multi-column spans aren't measured
                for _ in range(cell.behavior.colspan):
                    next(cols)
                    icol += 1


class TableColumn(Behavior):
    __slots__ = ('width',)

    def __init__(self, box):
        super().__init__(box)
        self.width = box.attrs.get('width', '')

    @property
    def text_allowed(self):
        return False

    @property
    def is_fixed(self):
        return all(n in '0123456789' for n in self.width)

    @property
    def fixed(self):
        return int(self.width)

    @property
    def is_max_content(self):
        return self.width in ('0*', 'max-content')

    @property
    def is_min_content(self):
        return self.width in ('min-content',)

    @property
    def is_proportional(self):
        return self.width.endswith('*') and self.width != '0*'

    @property
    def proportion(self):
        return int(self.width[:-1])

    def measure(self, row):
        if self.is_fixed:
            return self.fixed
        elif self.is_max_content:
            return row.wrap(None, 1000)[0]
        elif self.is_min_content:
            return row.wrap(None, 0)[0]
        return 0


class TableRowGroup(Behavior):
    __slots__ = ('drawn_on',)

    def __init__(self, box):
        super().__init__(box)
        self.drawn_on = None

    @property
    def text_allowed(self):
        return False

    def add(self, child):
        if self.box.parent.buffered:
            self.box.children.append(child)

    def wrap(self, page, available_width):
        header_height = 0
        for row in self.box.children:
            header_height += row.behavior._wrap(page, available_width)[1]
        return header_height

    def draw(self, page, x, y):
        self.drawn_on = page.page_number
        for row in self.box.children:
            x, y = row.behavior._draw(page, x, y)
        self.box.position += 1
        return x, y


class TableRow(Behavior):
    __slots__ = ()

    @property
    def text_allowed(self):
        return False

    @property
    def table_row_frame_top(self):
        if self.collapsed:
            return self.style.border_top_width
        return 0

    @property
    def table_row_frame_right(self):
        return 0

    @property
    def table_row_frame_bottom(self):
        if self.collapsed:
            return self.style.border_bottom_width
        return 0

    @property
    def table_row_frame_left(self):
        return 0

    def wrap(self, page, available_width):
        table = self.box.parent.parent.behavior
        return available_width, (
            table.reserve_header_height(page, available_width) +
            self._wrap(page, available_width)[1] +
            table.reserve_footer_height(page, available_width)
        )

    def _wrap(self, page, available_width):
        table = self.box.parent.parent.behavior
        children = self.box.children
        column_widths = table.get_column_widths(available_width)
        self.box.width = available_width
        cell_widths = self.box.lines = []

        if not children:
            return 0, 0

        col_width = iter(column_widths)
        for cell in children:
            if not cell or cell.behavior.colspan == 1:
                cell_widths.append(next(col_width))
            else:
                cell_widths.append(0)
                for col in range(cell.behavior.colspan):
                    # TODO: re-implement cell_spacing
                    cell_widths[-1] += next(col_width)  # + self.box.cell_spacing / 2.0

        max_height = 0
        for cell, cell_width in zip(children, cell_widths):
            if cell is not None:
                # TODO: re-implement collapsed
                #cell.collapsed = self.collapsed
                _, height = cell.wrap(page, cell_width)
                max_height = max(max_height, height)

        for cell in children:
            if not cell: continue
            cell.height = max_height

        self.box.height = self.box.frame_height + max_height
        return self.box.width, self.box.height

    def split(self, top_parent, bottom_parent, available_height):
        if available_height >= self.box.height:
            return self, None

        content_height = available_height - self.box.frame_height
        top_half = Box(self.box.parent, self.box.tag, self.box.attrs)
        top_half.behavior = self.box.behavior
        top_half.position = self.box.position
        top_half.position_of_type = self.box.position_of_type
        bottom_half = Box(self.box.parent, self.box.tag, self.box.attrs)
        bottom_half.behavior = self.box.behavior
        bottom_half.position = self.box.position+1
        bottom_half.position_of_type = self.box.position_of_type+1

        for cell in self.box.children:
            if cell:
                cell.split(top_half, bottom_half, content_height)

        if any(c.children for c in bottom_half.children if c):
            bottom_half.last = self.box.last
            return top_half, bottom_half
        top_half.last = self.box.last
        return top_half, None

    def draw(self, page, x, y):
        table = self.box.parent.parent
        x, y = table.behavior.draw_header(page, x, y)
        x, y = self._draw(page, x, y)
        return x, y

    def _draw(self, page, x, y):
        original_x, original_y = x, y
        # TODO: re-implement cell_spacing
        #x += self.cell_spacing / 2.0
        #y -= self.height
        y -= self.box.frame_top
        children = self.box.children
        cell_widths = self.box.lines
        last = len(cell_widths)-1
        for i, (cell, width) in enumerate(zip(children, cell_widths)):
            if cell:
                #if False and self.collapsed:
                #    self.draw_collapsed_cell_border(
                #        None if i == 0 else self.children[i-1],
                #        cell,
                #        None if i == last else self.children[i+1],
                #    )
                #else:
                cell.draw_border_and_background(page, x, original_y - self.box.height)
                cell.draw(page, x, y)
            # TODO: re-implement cell_spacing
            x += width #+ self.cell_spacing / 2.0
        return original_x, original_y - self.box.height

    def draw_collapsed_cell_border(self, before, cell, after):
        pass


class TableCell(Behavior):
    __slots__ = ('colspan',)

    def __init__(self, box):
        super().__init__(box)
        self.colspan = box.attrs.get('colspan', None)
        if self.colspan is not None:
            self.colspan = int(self.colspan)
            assert self.colspan > 0
        else:
            self.colspan = 1

    @property
    def cell_frame_top(self):
        s = self.style
        if self.collapsed:
            return s.border_top_width/2 + s.padding_top
        else:
            return s.border_top_width + s.padding_top

    @property
    def cell_frame_right(self):
        s = self.style
        if self.collapsed:
            return s.padding_right + s.border_right_width/2.0
        else:
            return s.padding_right + s.border_right_width

    @property
    def cell_frame_bottom(self):
        s = self.style
        if self.collapsed:
            return s.border_bottom_width/2.0 + s.padding_bottom
        else:
            return s.border_bottom_width + s.padding_bottom

    @property
    def cell_frame_left(self):
        s = self.style
        if self.collapsed:
            return s.border_left_width/2.0 + s.padding_left
        else:
            return s.border_left_width + s.padding_left

    @property
    def cell_border_box(self):
        return (
            (0, self.height),  # top left
            (self.width, self.height),  # top right
            (0, 0),  # bottom left
            (self.width, 0),  # bottom right
        )

    def cell_draw(self, page, x, y):
        x += self.frame_left
        if self.style.vertical_align == VerticalAlign.top:
            y -= self.frame_top
        elif self.style.vertical_align == VerticalAlign.middle:
            y -= (self.height + sum(self.content_heights)) / 2.0
        else:
            y -= self.height - (sum(self.content_heights) + self.frame_bottom)

        for block, height in zip(self.children, self.content_heights):
            block.draw(page, x, y)
            y -= height

    def cell_wrap(self, page, available_width):
        self.width = available_width
        self.content_heights = []

        self.css.apply(self)
        if self.parent:
            self.style = self.style.inherit(self.parent.style)

        content_width = available_width - self.frame_width

        consumed = 0
        for block in self.children:
            _, height = block.wrap(page, content_width)
            consumed += height
            self.content_heights.append(height)

        self.height = self.frame_height + consumed
        return available_width, self.height

    def cell_split(self, top_parent, bottom_parent, available_height):

        if not self.content_heights:
            self.parent = top_parent
            top_parent.children.append(self)
            bottom_parent.children.append(None)
            return

        if self.style.vertical_align == VerticalAlign.top:
            consumed_height = self.frame_top
        elif self.style.vertical_align == VerticalAlign.middle:
            consumed_height = (self.height - sum(self.content_heights)) / 2.0
        else:
            consumed_height = self.height - (sum(self.content_heights) + self.frame_bottom)

        if consumed_height >= available_height:
            # border and padding don't even fit
            top_parent.children.append(None)
            self.parent = bottom_parent
            bottom_parent.children.append(self)
            return

        split_at_block, split_block_height = -1, 0
        for split_at_block, split_block_height in enumerate(self.content_heights):
            consumed_height += split_block_height
            if consumed_height >= available_height:
                break

        if consumed_height <= available_height:
            if len(self.children) == 1 or len(self.children)-1 == split_at_block:
                self.parent = top_parent
                top_parent.children.append(self)
                bottom_parent.children.append(None)
                return
            else:
                top_cell = Cell(self.tag, top_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)
                for top_child in self.children[:split_at_block+1]:
                    top_child.parent = top_cell
                    top_cell.children.append(top_child)
                bottom_cell = Cell(self.tag, bottom_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)
                for bottom_child in self.children[split_at_block-1:]:
                    bottom_child.parent = bottom_cell
                    bottom_cell.children.append(bottom_child)
                return top_cell, bottom_cell

        top_cell = Cell(self.tag, top_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)
        for top_child in self.children[:split_at_block]:
            top_child.parent = top_cell
            top_cell.children.append(top_child)

        block = self.children[split_at_block]
        bottom_cell = Cell(self.tag, bottom_parent, self.id, self.classes, self.css, self.position, colspan=self.colspan)

        block.split(top_cell, bottom_cell, available_height - (consumed_height - split_block_height))

        for bottom_child in self.children[split_at_block+1:]:
            bottom_child.parent = bottom_cell
            bottom_cell.children.append(bottom_child)

        return top_cell, bottom_cell
