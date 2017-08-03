from pdfrw.objects import PdfObject, PdfString


def serialize(meta):
    if isinstance(meta, dict):
        yield b'<<'
        for key, value in meta.items():
            if not key.startswith('/'):
                key = '/'+key
            yield '{} '.format(key).encode()
            yield from serialize(value)
            yield b' '
        yield b'>>'
    elif isinstance(meta, (PdfObject, PdfString)):
        yield str(meta).encode()
    elif isinstance(meta, str):
        if meta.startswith('(') and meta.endswith(')'):
            pass
        elif not meta.startswith('/'):
            meta = '/'+meta
        yield meta.encode()
    elif isinstance(meta, list):
        yield b'[ '
        for value in meta:
            yield from serialize(value)
            yield b' '
        yield b']'
    else:
        yield str(meta).encode()


class PDFReference:

    def __init__(self, id, meta=None, name=None):
        self.id = id
        self.meta = meta or {}
        self.gen = 0
        self.chunks = []
        self.offset = None
        self.name = name

    def update(self, dict):
        self.meta.update(dict)

    def write(self, chunk):
        self.meta.setdefault('Length', 0)
        self.meta['Length'] += len(chunk)
        self.chunks.append(chunk)

    def read(self):
        yield "{r.id} {r.gen} obj\n".format(r=self).encode()
        yield from self.read_meta()
        if self.chunks and not self.chunks[-1].endswith(b'\n'):
            self.write(b'\n')
        if self.chunks:
            yield b"stream\n"
            yield from self.chunks
            yield b"endstream\n"
            del self.chunks
        yield b"endobj\n"

    def read_meta(self):
        yield from serialize(self.meta)
        yield b"\n"

    @property
    def has_content(self):
        return bool(self.chunks)

    def __str__(self):
        return "{r.id} {r.gen} R".format(r=self)
