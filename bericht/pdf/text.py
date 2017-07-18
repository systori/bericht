from reportlab.pdfbase import pdfmetrics
from reportlab.lib.rl_accel import escapePDF


class PDFText:

    def __init__(self, page, x=0, y=0):
        self.page = page
        self.write("BT")
        self.set_position(x, y)
        self.font = None
        self.font_metrics = None

    def write(self, code):
        self.page.write(code+'\n')

    def set_position(self, x=0, y=0):
        self.write("{} {} Td".format(x, y))

    def set_font(self, font, size, leading):
        self.font = font
        self.font_metrics = pdfmetrics.getFont(font.name)
        self.page.font[font.id] = font.description
        self.write("/{} {} Tf {} TL".format(font.id, size, leading))

    def line(self, txt, new_line=False):
        font = self.font_metrics
        for f, t in pdfmetrics.unicode2T1(txt, [font]+font.substitutionFonts):
            self.write("(%s) Tj " % escapePDF(t))
        if new_line:
            self.write(' T*')

    def close(self):
        self.write("ET")
