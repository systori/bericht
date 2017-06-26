class PDFFont:

    def __init__(self, document, name, id):
        self.name = name
        self.id = id
        self.description = document.ref({
            'Type': 'Font',
            'BaseFont': name,
            'Subtype': 'Type1',
            'Encoding': 'WinAnsiEncoding'
        })
