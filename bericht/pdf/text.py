class PDFText:

    def __init__(self, page, x=0, y=0):
        self.page = page
        self.write("BT")
        self.font = self.page.document.font.id
        self.set_position(x, y)

    def write(self, code):
        self.page.write(code+'\n')

    def set_position(self, x=0, y=0):
        self.write("{} {} Td".format(x, y))

    def set_font(self, font):
        self.write("/{} 12 Tf 14 TL".format(font))
    font = property(None, set_font)

    def line(self, txt, new_line=False):
        self.write("({}) Tj{}".format(txt, (new_line and ' T*' or '')))

    def close(self):
        self.write("ET")
