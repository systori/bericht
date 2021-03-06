from .font import getFont
from reportlab.lib.rl_accel import escapePDF
from reportlab.pdfbase import pdfmetrics


class PDFText:

    def __init__(self, page, x=0, y=0):
        self.page = page
        self.write("BT\n")
        self.set_position(x, y)
        self.font_name = None
        self.font_size = None
        self.font_leading = None
        self.font_subset = None

    def write(self, code):
        self.page.write(code)

    def move_position(self, dx=0, dy=0):
        self.write("{} {} Td\n".format(dx, dy))

    def set_position(self, x=0, y=0):
        self.write("1 0 0 1 {} {} Tm\n".format(x, y))

    def set_font(self, font_name, size, leading):
        self.font_name = font_name
        self.font_size = size
        self.font_leading = leading
        self.font_subset = None

    def draw(self, txt, new_line=False):
        doc = self.page.document
        font = getFont(self.font_name)
        if font._dynamicFont:
            for subset, t in font.splitString(txt, doc):
                if self.font_subset != subset:
                    name = font.getSubsetInternalName(subset, doc)
                    if name not in doc.font_references:
                        doc.font_references[name] = doc.ref()
                    if name not in self.page.font:
                        self.page.font[name] = doc.font_references[name]
                    self.write("{} {} Tf {} TL\n".format(
                        name, self.font_size, self.font_leading
                    ))
                self.write("({}) Tj ".format(escapePDF(t)))
        elif font._multiByte:
            name = doc.fontMapping.get(font.fontName)
            if name is None:
                name = doc.fontMapping[font.fontName] = '/F{}'.format(len(doc.fontMapping)+1)
                doc.delayedFonts.append(font)
            if name not in doc.font_references:
                doc.font_references[name] = doc.ref()
            if name not in self.page.font:
                self.page.font[name] = doc.font_references[name]
            self.write("/{} {} Tf {} TL\n".format(name, self.font_size, self.font_leading))
            self.write("(%s) Tj ".format(font.formatForPdf(txt)))
        else:
            _font = None
            for f, t in pdfmetrics.unicode2T1(txt, [font]+font.substitutionFonts):
                if f != _font:
                    name = doc.fontMapping.get(f.fontName)
                    if name is None:
                        name = doc.fontMapping[f.fontName] = '/F{}'.format(len(doc.fontMapping)+1)
                        doc.delayedFonts.append(f)
                    if name not in doc.font_references:
                        doc.font_references[name] = doc.ref()
                    if name not in self.page.font:
                        self.page.font[name] = doc.font_references[name]
                    self.write("{} {} Tf {} TL\n".format(name, self.font_size, self.font_leading))
                    _font = f
                self.write("({}) Tj ".format(escapePDF(t)))

        if new_line:
            self.write('T*\n')

    def close(self):
        self.write("ET\n")
