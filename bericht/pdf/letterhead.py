from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj

__all__ = ('PDFLetterhead',)


class PDFLetterhead:

    def __init__(self, document, path):
        self.document = document
        self.pages = []
        template = PdfReader(path)
        letterhead_num = 1
        for page in template.pages:
            template_page = pagexobj(page)
            form = document.ref({
                'Type': 'XObject',
                'Subtype': 'Form',
                'FormType': 1,
                'BBox': template_page.BBox,
                'Filter': 'FlateDecode',
            }, name='Letterhead{}'.format(letterhead_num))
            form.write(template_page.stream.encode('Latin-1'))
            self.pages.append(form)
            letterhead_num += 1

    def read(self):
        for page in self.pages:
            yield from self.document.finalize_reference(page)

    def __getitem__(self, item):
        if item < 1:
            return self.pages[0]
        if item >= len(self.pages):
            return self.pages[-1]
        return self.pages[item]
