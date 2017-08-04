from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj

__all__ = ('PDFLetterhead',)


class XObject:

    def __init__(self, doc, xobj, name=None):
        self.doc = doc
        self.name = name
        self.form = form = doc.ref({
            'Type': 'XObject',
            'Subtype': 'Form',
            'FormType': 1,
            'BBox': xobj.BBox,
            'Resources': {}
        }, name=name)
        if xobj.Filter:
            form.meta['Filter'] = 'FlateDecode'
        if xobj.Resources.Font:
            form.meta['Resources']['Font'] = dict(self.copy_fonts(xobj.Resources.Font))
        if xobj.Resources.ExtGState:
            form.meta['Resources']['ExtGState'] = xobj.Resources.ExtGState
        if xobj.Resources.XObject:
            form.meta['Resources']['XObject'] = dict(self.copy_xobjects(xobj.Resources.XObject))
        form.write(xobj.stream.encode('latin'))

    def copy_fonts(self, fonts):

        for font_id, font_ref in fonts.iteritems():

            font = self.doc.ref({
                key: font_ref[key] for key in
                set(font_ref.keys()) - {'/ToUnicode', '/FontDescriptor', '/DescendantFonts'}
            })

            if font_ref.ToUnicode:
                font.meta['ToUnicode'] = self.doc.ref()
                font.meta['ToUnicode'].write(font_ref.ToUnicode.stream.encode('latin'))

            if font_ref.FontDescriptor:
                font.meta['FontDescriptor'] = self.copy_font_descriptor(font_ref.FontDescriptor)

            if font_ref.DescendantFonts:
                dfs = font.meta['DescendantFonts'] = []
                for descendant in font_ref.DescendantFonts:
                    dfont = self.doc.ref({
                        key: descendant[key] for key in
                        set(descendant.keys()) - {'/FontDescriptor'}
                    })
                    dfont.meta['FontDescriptor'] = self.copy_font_descriptor(descendant.FontDescriptor)
                    dfs.append(dfont)

            yield font_id, font

    def copy_font_descriptor(self, descriptor):
        fd = self.doc.ref()
        for key, value in descriptor.iteritems():
            if key.startswith('/FontFile'):
                ff = self.doc.ref({
                    key: value for key, value in value.iteritems()
                    if key in ('/Filter', '/Subtype')
                })
                ff.write(value.stream.encode('latin'))
                fd.meta[key] = ff
            elif key.startswith('/CIDSet'):
                cidset = self.doc.ref({
                    key: value for key, value in value.iteritems()
                    if key in ('/Filter', '/Subtype')
                })
                cidset.write(value.stream.encode('latin'))
                fd.meta[key] = cidset
            else:
                fd.meta[key] = value
        return fd

    def copy_xobjects(self, xobjs):
        for xobj_id, xobj_ref in xobjs.iteritems():
            xobj = XObject(self.doc, xobj_ref)
            yield xobj_id, xobj.form


class PDFLetterhead:

    def __init__(self, document, path):
        self.document = document
        self.pages = []
        self.refs = []
        template = PdfReader(path)
        letterhead_num = 1
        for page in template.pages:
            xobject = XObject(self, pagexobj(page), name='Letterhead{}'.format(letterhead_num))
            self.pages.append(xobject.form)
            letterhead_num += 1

    def ref(self, *args, **kwargs):
        ref = self.document.ref(*args, **kwargs)
        self.refs.append(ref)
        return ref

    def read(self):
        for obj in self.refs:
            yield from self.document.finalize_reference(obj)

    def __getitem__(self, item):
        if item < 1:
            return self.pages[0]
        if item >= len(self.pages):
            return self.pages[-1]
        return self.pages[item]
