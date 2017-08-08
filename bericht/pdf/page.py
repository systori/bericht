from .text import PDFText
from bericht.node.text import stringWidth

__all__ = ('PDFPage',)


class PDFPage:

    tag = '@page'

    def __init__(self, document, page_number, css, size='letter', layout='portrait'):
        self.parent = None
        self.classes = []
        self.style = None
        self.position = page_number
        css.apply(self)

        self.document = document
        self.size = size
        self.layout = layout

        dimensions = SIZES[self.size.upper()]
        self.width = dimensions[0 if self.layout is 'portrait' else 1]
        self.height = dimensions[1 if self.layout is 'portrait' else 0]

        margins = DEFAULT_MARGINS.copy()
        if self.style:
            for side in ('top', 'right', 'bottom', 'left'):
                attr = 'margin_'+side
                if attr in self.style.set_attrs:
                    margins[side] = getattr(self.style, attr)
        self.x = margins['left']
        self.y = self.height - margins['top']
        self.available_width = self.width - self.x - margins['right']
        self.margins = margins

        self.content = document.ref()

        # Initialize the Font, XObject, and ExtGState dictionaries
        self.resources = document.ref({
            'ProcSet': ['PDF', 'Text', 'ImageB', 'ImageC', 'ImageI'],
        })

        if self.style and 'letterhead_page' in self.style.set_attrs and self.document.letterhead:
            letterhead_page = self.document.letterhead[int(self.style.letterhead_page)-1]
            self.resources.meta.update({
                'XObject': {letterhead_page.name: letterhead_page}
            })
            self.write('/{} Do\n'.format(letterhead_page.name))

        # The page dictionary
        self.dictionary = document.ref({
            'Type': 'Page',
            'Parent': document.root.meta['Pages'],
            'MediaBox': [0, 0, self.width, self.height],
            'Contents': self.content,
            'Resources': self.resources,
        })

        if self.style.page_bottom_right_content:
            style = self.style.set(font_size=9)
            page_text = self.style.page_bottom_right_content(self)
            text_width = stringWidth(page_text, style.font_name, style.font_size)
            text = self.begin_text(
                (self.margins['left'] + self.available_width) - text_width,
                self.margins['bottom'] - style.leading*2
            )
            text.set_font(style.font_name, style.leading, style.font_size)
            text.draw(page_text)
            text.close()

    @property
    def page_number(self):
        return self.position

    @property
    def has_content(self):
        return self.content.has_content

    @property
    def available_height(self):
        return self.y - self.margins['bottom']

    @property
    def font(self):
        if 'Font' not in self.resources.meta:
            self.resources.meta['Font'] = {}
        return self.resources.meta['Font']

    def write(self, chunk):
        self.content.write(chunk.encode())

    def read(self):
        for ref in (self.dictionary, self.resources, self.content):
            yield from self.document.finalize_reference(ref)

    def save_state(self):
        self.write("q\n")

    def restore_state(self):
        self.write("Q\n")

    def translate(self, x, y):
        self.write("1 0 0 1 {} {} cm\n".format(x, y))

    def begin_text(self, x, y):
        return PDFText(self, x, y)

    def line_width(self, width):
        self.write("{} w\n".format(width))

    def stroke_color(self, r, g, b, a):
        assert a == 1, "TODO: implement alpha"
        self.write("{} {} {} RG\n".format(r, g, b))

    def line(self, x1, y1, x2, y2):
        self.write("n {} {} m {} {} l S\n".format(x1, y1, x2, y2))

    def fill_color(self, r, g, b, a):
        assert a == 1, "TODO: implement alpha"
        self.write("{} {} {} rg\n".format(r, g, b))

    def rectangle(self, x, y, width, height):
        self.write("n {} {} {} {} re f*\n".format(x, y, width, height))


DEFAULT_MARGINS = {
    'top': 72,
    'left': 72,
    'bottom': 72,
    'right': 72
}

SIZES = {
    '4A0': [4767.87, 6740.79],
    '2A0': [3370.39, 4767.87],
    'A0': [2383.94, 3370.39],
    'A1': [1683.78, 2383.94],
    'A2': [1190.55, 1683.78],
    'A3': [841.89, 1190.55],
    'A4': [595.28, 841.89],
    'A5': [419.53, 595.28],
    'A6': [297.64, 419.53],
    'A7': [209.76, 297.64],
    'A8': [147.40, 209.76],
    'A9': [104.88, 147.40],
    'A10': [73.70, 104.88],
    'B0': [2834.65, 4008.19],
    'B1': [2004.09, 2834.65],
    'B2': [1417.32, 2004.09],
    'B3': [1000.63, 1417.32],
    'B4': [708.66, 1000.63],
    'B5': [498.90, 708.66],
    'B6': [354.33, 498.90],
    'B7': [249.45, 354.33],
    'B8': [175.75, 249.45],
    'B9': [124.72, 175.75],
    'B10': [87.87, 124.72],
    'C0': [2599.37, 3676.54],
    'C1': [1836.85, 2599.37],
    'C2': [1298.27, 1836.85],
    'C3': [918.43, 1298.27],
    'C4': [649.13, 918.43],
    'C5': [459.21, 649.13],
    'C6': [323.15, 459.21],
    'C7': [229.61, 323.15],
    'C8': [161.57, 229.61],
    'C9': [113.39, 161.57],
    'C10': [79.37, 113.39],
    'RA0': [2437.80, 3458.27],
    'RA1': [1729.13, 2437.80],
    'RA2': [1218.90, 1729.13],
    'RA3': [864.57, 1218.90],
    'RA4': [609.45, 864.57],
    'SRA0': [2551.18, 3628.35],
    'SRA1': [1814.17, 2551.18],
    'SRA2': [1275.59, 1814.17],
    'SRA3': [907.09, 1275.59],
    'SRA4': [637.80, 907.09],
    'EXECUTIVE': [521.86, 756.00],
    'FOLIO': [612.00, 936.00],
    'LEGAL': [612.00, 1008.00],
    'LETTER': [612.00, 792.00],
    'TABLOID': [792.00, 1224.00]
}