from .document import PDFDocument


class PDFStreamer:

    def __init__(self, block_generator):
        self.generator = block_generator
        self.pdf = PDFDocument()

    def __iter__(self):
        yield from self.pdf.header()
        page = self.pdf.add_page()
        page.remaining -= 100
        for block in self.generator:
            block.wrap(200)
            block.draw_on(page, 0, page.remaining)
            page.remaining -= block.height
        yield from page.read()
        yield from self.pdf.footer()
