from .document import PDFDocument


class PDFStreamer:

    def __init__(self, block_generator):
        self.generator = block_generator
        self.pdf = PDFDocument()

    def __iter__(self):
        yield from self.pdf.header()
        page = self.pdf.add_page()
        for block in self.generator:
            block.wrap(page.available_width)
            block.draw_on(page, page.x, page.y)
            page.y -= block.height
        yield from page.read()
        yield from self.pdf.footer()
