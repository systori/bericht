def serialize(meta):
    if isinstance(meta, dict):
        yield b'<<'
        for key, value in meta.items():
            yield '/{} '.format(key).encode()
            yield from serialize(value)
            yield b' '
        yield b'>>'
    elif isinstance(meta, str):
        yield ('/'+meta).encode()
    elif isinstance(meta, list):
        yield b'[ '
        for value in meta:
            yield from serialize(value)
            yield b' '
        yield b']'
    else:
        yield str(meta).encode()


class PDFReference:

    def __init__(self, id, meta=None):
        self.id = id
        self.meta = meta or {}
        self.gen = 0
        self.chunks = []

    def write(self, chunk):
        self.meta.setdefault('Length', 0)
        self.meta['Length'] += len(chunk)
        self.chunks.append(chunk)

    def read(self):
        yield "{r.id} {r.gen} obj\n".format(r=self).encode()
        yield from self.read_meta()
        if self.chunks:
            yield b"stream\n"
            yield from self.chunks
            yield b"endstream\n"
            del self.chunks
        yield b"endobj\n"

    def read_meta(self):
        yield from serialize(self.meta)
        yield b"\n"

    def __str__(self):
        return "{r.id} {r.gen} R".format(r=self)
