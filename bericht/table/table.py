from bericht.block import Block, LayoutError
from bericht.style import BorderCollapse


__all__ = ['Table']


class Table(Block):

    __slots__ = ('ratios', 'columns',)

    def __init__(self, ratios, columns, rows, style, was_split=False):
        super().__init__(rows, style, was_split)
        self.ratios = ratios
        self.columns = columns

    def draw(self):
        x = self.frame_left
        y = self.height - self.frame_top
        for row, height in zip(self.content, self.content_heights):
            y -= height
            row.drawOn(self.canv, x, y)
        self.draw_border()

    def calculate_ratio_columns(self, available_width):
        units = sum(self.ratios)
        if units == 0:
            self.content_widths = self.columns.copy()
        else:
            fixed = sum(self.columns)
            unit_size = (available_width - fixed) / units
            widths = []
            for ratio, column in zip(self.ratios, self.columns):
                if ratio == 0:
                    widths.append(column)
                else:
                    widths.append(ratio * unit_size)
            self.content_widths = widths

    def wrap(self, available_width, _=None):
        self.calculate_ratio_columns(available_width - self.frame_width)
        self.width = available_width
        self.height = self.frame_height
        self.content_heights = []
        collapsed = self.style.border_collapse == BorderCollapse.collapse
        for row in self.content:
            row.collapsed = collapsed
            _, height = row.wrap(self.content_widths)
            self.content_heights.append(height)
            self.height += height
        return available_width, self.height

    def split(self, available_width, available_height):
        if self.content_heights is None:
            self.wrap(available_width)

        assert self.content_heights, "Split called on empty table."

        split_at_row = -1
        split_row_height = consumed_height = 0
        for split_at_row, split_row_height in enumerate(self.content_heights):
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
                    Table(self.ratios, self.columns, self.content[:split_at_row+1], self.style, was_split=True),
                    Table(self.ratios, self.columns, self.content[split_at_row-1:], self.style, was_split=True)
                ]

        top_rows = self.content[:split_at_row]
        row = self.content[split_at_row]
        bottom_rows = self.content[split_at_row+1:]

        top_height = available_height - (consumed_height - split_row_height)
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
            Table(self.ratios, self.columns, top_rows, self.style, was_split=True),
            Table(self.ratios, self.columns, bottom_rows, self.style, was_split=True)
        ]
