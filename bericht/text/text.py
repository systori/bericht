from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import getSampleStyleSheet

__all__ = ['Text']

rlstyleSheet = getSampleStyleSheet()
rlstyle = rlstyleSheet['BodyText']


class Text(Flowable):

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.style = rlstyle
        self.words = text.split()
        self.lines = None

    def draw(self):
        font = self.style
        x, y = 0, self.height - font.fontSize*1.2
        txt = self.canv.beginText(x, y)
        txt.setFont(font.fontName, font.fontSize, font.leading)
        for line in self.lines:
            txt.textLine(' '.join(line))
        self.canv.drawText(txt)

    def wrap(self, available_width, available_height):
        self.width = available_width
        line = []
        line_width = 0
        self.lines = [line]
        space_width = stringWidth(' ', self.style.fontName, self.style.fontSize)
        for word in self.words:
            word_width = stringWidth(word, self.style.fontName, self.style.fontSize)
            if line_width+word_width > available_width:
                line = []
                line_width = 0
                self.lines.append(line)
            line_width += word_width + space_width
            line.append(word)
        self.height = len(self.lines) * self.style.leading
        return available_width, self.height
