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
                _, height_consumed = block.wrap(page, page.available_width)
                if height_consumed <= page.available_height:
                    block.draw(page, page.x, page.y)
                    page.y -= height_consumed
                    page.available_height -= height_consumed
                    break
                else:
                    yield from page.read()
                    page = self.pdf.add_page()
        yield from page.read()
        yield from self.pdf.footer()
