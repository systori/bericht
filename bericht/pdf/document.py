from .reference import PDFReference
from .letterhead import PDFLetterhead
from .page import PDFPage
from .font import PDFFont

__all__ = ('PDFDocument',)


class PDFDocument:

    def __init__(self, css, letterhead=None):
        self.css = css
        self.ref_ids = 0
        self.offset = 0
        self.references = []
        self.page = None
        self.fonts = {
            'Helvetica': PDFFont(self, 'Helvetica', 'F1'),
            'Helvetica-Bold': PDFFont(self, 'Helvetica-Bold', 'F2'),
            'Helvetica-BoldOblique': PDFFont(self, 'Helvetica-BoldOblique', 'F3'),
            'Helvetica-Oblique': PDFFont(self, 'Helvetica-Oblique', 'F4'),
        }
        self.root = self.ref({
            'Type': 'Catalog',
            'Pages': self.ref({
                'Type': 'Pages',
                'Count': 0,
                'Kids': []
            })
        })
        self.info = self.ref({
            'Producer': 'bericht',
        })
        self.letterhead = PDFLetterhead(self, letterhead) if letterhead else None

    def header(self):
        src = b"%PDF-1.7\n%\xc3\xbf\xc3\xbf\xc3\xbf\xc3\xbf\n"
        self.offset += len(src)
        yield src
        if self.letterhead:
            yield from self.letterhead.read()

    def finalize_reference(self, ref):
        ref.offset = self.offset
        for chunk in ref.read():
            self.offset += len(chunk)
            yield chunk

    @property
    def footer_refs(self):
        yield self.info
        for font in self.fonts.values():
            yield font.description
        yield self.root
        yield self.root.meta['Pages']

    def footer(self):
        for ref in self.footer_refs:
            yield from self.finalize_reference(ref)

        yield b"xref\n"
        yield "0 {}\n".format(len(self.references) + 1).encode()
        yield b"0000000000 65535 f \n"
        for ref in self.references:
            yield "{:0>10} 00000 n \n".format(ref.offset).encode()

        yield b"trailer\n"
        yield from self.ref({
            'Size': len(self.references) + 1,
            'Root': self.root,
            'Info': self.info
        }).read_meta()

        yield b"startxref\n"
        yield str(self.offset).encode()
        yield b"\n%%EOF\n"

    def ref(self, meta=None, name=None):
        self.ref_ids += 1
        ref = PDFReference(self.ref_ids, meta, name)
        self.references.append(ref)
        return ref

    def add_page(self):
        pages = self.root.meta['Pages'].meta
        pages['Count'] += 1
        self.page = PDFPage(self, pages['Count'], self.css, 'a4')
        pages['Kids'].append(self.page.dictionary)
        return self.page
