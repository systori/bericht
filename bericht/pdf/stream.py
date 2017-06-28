from .document import PDFDocument


class PDFStreamer:

    def __init__(self, block_generator):
        self.generator = block_generator
        self.pdf = PDFDocument()

    def __iter__(self):
        yield from self.pdf.header()
        page = self.pdf.add_page()
        for block in self.generator:
            while True:
                block.wrap(page.available_width)
                if block.height <= page.available_height:
                    page.y -= block.height
                    page.available_height -= block.height
                    block.draw(page, page.x, page.y)
                    break
                else:
                    yield from page.read()
                    page = self.pdf.add_page()
        yield from page.read()
        yield from self.pdf.footer()
