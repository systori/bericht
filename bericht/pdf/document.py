from .reference import PDFReference
from .page import PDFPage
from .font import PDFFont

__all__ = ('PDFDocument',)


class PDFDocument:

    def __init__(self):
        self.ref_ids = 0
        self.offset = 0
        self.offsets = []
        self.page = None
        self.font = PDFFont(self, 'Helvetica', 'F1')
        self.font_families = {self.font.name: self.font}
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

    def header(self):
        src = (
            b"%PDF-1.7\n"
            b"%\xFF\xFF\xFF\xFF\n"
        )
        self.offset += len(src)
        yield src

    def finalize_reference(self, ref):
        self.offsets.append(self.offset)
        for chunk in ref.read():
            self.offset += len(chunk)
            yield chunk

    @property
    def footer_refs(self):
        yield self.info
        for font in self.font_families.values():
            yield font.description
        yield self.root
        yield self.root.meta['Pages']

    def footer(self):
        for ref in self.footer_refs:
            yield from self.finalize_reference(ref)

        yield b"xref\n"
        yield "0 {}\n".format(len(self.offsets) + 1).encode()
        yield b"0000000000 65535 f \n"
        for offset in self.offsets:
            yield "{:0>10} 00000 n \n".format(offset).encode()

        yield b"trailer\n"
        yield from self.ref({
            'Size': len(self.offsets) + 1,
            'Root': self.root,
            'Info': self.info
        }).read_meta()

        yield b"startxref\n"
        yield str(self.offset).encode()
        yield b"\n%%EOF\n"

    def ref(self, meta=None):
        self.ref_ids += 1
        return PDFReference(self.ref_ids, meta)

    def add_page(self):
        pages = self.root.meta['Pages'].meta
        pages['Count'] += 1
        self.page = PDFPage(self, pages['Count'])
        pages['Kids'].append(self.page.dictionary)
        return self.page
