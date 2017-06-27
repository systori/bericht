class PDFText:

    def __init__(self, page, x=0, y=0):
        self.page = page
        self.write("BT")
        self.font = self.page.document.font.id

    def write(self, code):
        self.page.write(code+'\n')

    def set_x(self, x):
        self.write("{} 0 Td".format(x))
    x = property(None, set_x)

    def set_font(self, font):
        self.write("/{} 12 Tf 14 TL".format(font))
    font = property(None, set_font)

    def line(self, txt, new_line=False):
        self.write("({}) Tj{}".format(txt, (new_line and ' T*' or '')))

    def close(self):
        self.write("ET")
