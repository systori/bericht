from reportlab.pdfbase.pdfmetrics import getFont, Font
from reportlab.pdfbase.ttfonts import TTFont, makeToUnicodeCMap

__all__ = ('getFont', 'read_font')


def read_font(doc, font):
    if isinstance(font, TTFont):
        yield from read_truetype(doc, font)
    elif isinstance(font, Font):
        yield from read_type1(doc, font)
    else:
        raise RuntimeError


def read_type1(doc, font):
    name = doc.fontMapping[font.fontName]
    ref = doc.font_references[name]
    ref.update({
        'Type': 'Font',
        'Subtype': 'Type1',
        'BaseFont': font.fontName,
        'Encoding': 'WinAnsiEncoding'
    })
    yield from doc.finalize_reference(ref)


# PDF font flags (see PDF Reference Guide table 5.19)
FF_SYMBOLIC = 1 << 3-1
FF_NONSYMBOLIC = 1 << 6-1


def SUBSETN(n, table=bytes.maketrans(b'0123456789', b'ABCDEFGIJK')):
    return bytes('%6.6d' % n, 'ASCII').translate(table)


def read_truetype(doc, font):
    state = font.state[doc]
    for n, subset in enumerate(state.subsets):
        internalName = font.getSubsetInternalName(n, doc)[1:]
        baseFontName = (b''.join((SUBSETN(n), b'+', font.face.name, font.face.subfontNameX))).decode('pdfdoc')

        fontFile = doc.ref()
        fontFile.write(font.face.makeSubset(subset))
        fontFile.meta['Length1'] = fontFile.meta['Length']
        yield from doc.finalize_reference(fontFile)

        flags = font.face.flags & ~ FF_NONSYMBOLIC
        flags = flags | FF_SYMBOLIC

        FontDescriptor = doc.ref({
            'Type': '/FontDescriptor',
            'Ascent': font.face.ascent,
            'CapHeight': font.face.capHeight,
            'Descent': font.face.descent,
            'Flags': flags,
            'FontBBox': font.face.bbox,
            'FontName': baseFontName,
            'ItalicAngle': font.face.italicAngle,
            'StemV': font.face.stemV,
            'FontFile2': fontFile,
        })
        yield from doc.finalize_reference(FontDescriptor)

        cmapStream = doc.ref()
        cmapStream.write(makeToUnicodeCMap(baseFontName, subset).encode())
        yield from doc.finalize_reference(cmapStream)

        font_ref = doc.font_references['/'+internalName]
        font_ref.update({
            'Type': 'Font',
            'Subtype': 'TrueType',
            'Name': internalName,
            'BaseFont': baseFontName,
            'FirstChar': 0,
            'LastChar': len(subset) - 1,
            'Widths': list(map(font.face.getCharWidth, subset)),
            'ToUnicode': cmapStream,
            'FontDescriptor': FontDescriptor,
        })
        yield from doc.finalize_reference(font_ref)
