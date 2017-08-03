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
                'Resources': {'Font': fonts}
            }, name='Letterhead{}'.format(letterhead_num))
            if template_page.Filter:
                form.meta['Filter'] = 'FlateDecode'
            if template_page.Resources.ExtGState:
                form.meta['Resources']['ExtGState'] = template_page.Resources.ExtGState
            form.write(template_page.stream.encode('latin'))
            self.pages.append(form)
            letterhead_num += 1

    def get_fonts(self, page):
        doc = self.document
        fonts = {}
        for font_id, font_ref in page.Resources.Font.iteritems():

            font = fonts[font_id] = doc.ref({
                key: font_ref[key] for key in
                set(font_ref.keys()) - {'/ToUnicode', '/FontDescriptor', '/DescendantFonts'}
            })
            self.font_objects.append(fonts[font_id])

            if font_ref.ToUnicode:
                font.meta['ToUnicode'] = doc.ref()
                font.meta['ToUnicode'].write(font_ref.ToUnicode.stream.encode('latin'))
                self.font_objects.append(font.meta['ToUnicode'])

            if font_ref.FontDescriptor:
                font.meta['FontDescriptor'] = self.get_font_descriptor(font_ref.FontDescriptor)

            if font_ref.DescendantFonts:
                dfs = font.meta['DescendantFonts'] = []
                for descendant in font_ref.DescendantFonts:
                    dfont = doc.ref({
                        key: descendant[key] for key in
                        set(descendant.keys()) - {'/FontDescriptor'}
                    })
                    dfont.meta['FontDescriptor'] = self.get_font_descriptor(descendant.FontDescriptor)
                    dfs.append(dfont)
                    self.font_objects.append(dfont)

        return fonts

    def get_font_descriptor(self, descriptor):
        fd = self.document.ref()
        for key, value in descriptor.iteritems():
            if key.startswith('/FontFile'):
                ff = self.document.ref({
                    key: value for key, value in value.iteritems()
                    if key in ('/Filter', '/Subtype')
                })
                ff.write(value.stream.encode('latin'))
                self.font_objects.append(ff)
                fd.meta[key] = ff
            elif key.startswith('/CIDSet'):
                cidset = self.document.ref({
                    key: value for key, value in value.iteritems()
                    if key in ('/Filter', '/Subtype')
                })
                cidset.write(value.stream.encode('latin'))
                self.font_objects.append(cidset)
                fd.meta[key] = cidset
            else:
                fd.meta[key] = value
        self.font_objects.append(fd)
        return fd

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
