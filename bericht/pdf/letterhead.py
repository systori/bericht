from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj

__all__ = ('PDFLetterhead',)


class PDFLetterhead:

    def __init__(self, document, path):
        self.document = document
        self.pages = []
        self.font_objects = []
        template = PdfReader(path)
        letterhead_num = 1
        for page in template.pages:
            template_page = pagexobj(page)
            fonts = self.get_fonts(template_page)
            form = document.ref({
                'Type': 'XObject',
                'Subtype': 'Form',
                'FormType': 1,
                'BBox': template_page.BBox,
                'Filter': 'FlateDecode',
                'Resources': {'Font': fonts}
            }, name='Letterhead{}'.format(letterhead_num))
            form.write(template_page.stream.encode('latin'))
            self.pages.append(form)
            letterhead_num += 1

    def get_fonts(self, page):
        doc = self.document
        fonts = {}
        for font_id, font_ref in page.Resources.Font.iteritems():

            font = fonts[font_id] = doc.ref({
                key: font_ref[key] for key in
                set(font_ref.keys()) - {'/ToUnicode', '/FontDescriptor'}
            })
            self.font_objects.append(fonts[font_id])

            font.meta['ToUnicode'] = doc.ref()
            font.meta['ToUnicode'].write(font_ref.ToUnicode.stream.encode('latin'))
            self.font_objects.append(font.meta['ToUnicode'])

            fd = font.meta['FontDescriptor'] = doc.ref()
            for key, value in font_ref.FontDescriptor.iteritems():
                if key.startswith('/FontFile'):
                    ff = doc.ref({
                        key: value for key, value in value.iteritems()
                        if key in ('/Filter', '/Subtype')
                    })
                    ff.write(value.stream.encode('latin'))
                    self.font_objects.append(ff)
                    fd.meta[key] = ff
                else:
                    fd.meta[key] = value
            self.font_objects.append(fd)

        return fonts

    def read(self):
        for obj in self.font_objects:
            yield from self.document.finalize_reference(obj)
        for page in self.pages:
            yield from self.document.finalize_reference(page)

    def __getitem__(self, item):
        if item < 1:
            return self.pages[0]
        if item >= len(self.pages):
            return self.pages[-1]
        return self.pages[item]
