from .document import PDFDocument


class PDFStreamer:

    def __init__(self, block_generator, letterhead=None):
        self.generator = block_generator
        self.pdf = PDFDocument(block_generator.css, letterhead)

    def __iter__(self):
        yield from self.pdf.header()
        page = None
        for block in self.generator:
            while True:
                page = page or self.pdf.add_page()
                _, requested_height = block.wrap(page, page.available_width)
                if requested_height <= page.available_height:
                    page.x, page.y = block.draw(page, page.x, page.y)
                    break
                else:
                    #remainder, block = block.split(page)
                    #if remainder:
                    #    assert remainder.wrap(page)
                    #    remainder.draw(page)
                    assert page.has_content
                    yield from page.read()
                    page = None
        if page:
            yield from page.read()
        yield from self.pdf.footer()
