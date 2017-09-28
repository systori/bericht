from unittest import TestCase

from reportlab.pdfgen.canvas import Canvas

from bericht.html import HTMLParser
from bericht.node import Paragraph, Break


class BaseTestCase(TestCase):

    def draw(self, p):
        canvas = Canvas(None)
        p.wrapOn(canvas, 200, 100)
        p.canv = canvas
        p.draw()
        return canvas._code[0]

    def assertPDF(self, input, output):
        self.assertEqual(self.draw(input), ' '.join(output))

    @staticmethod
    def parse(html):
        return next(iter(HTMLParser(iter(html if isinstance(html, list) else [html]))))


class TestFormattingTagParsing(BaseTestCase):

    def test_bold_italic_underline(self):

        p = self.parse(
            '<p><b>hello</b> <i>world</i>, <u>bericht</u>! '
            '<strong>strong</strong> <b><i><u>biu</u></i></b></p>'
        )

        self.assertIsInstance(p, Paragraph)

        words = p.words
        self.assertEqual(len(words), 5)

        bold, italic, underline, strong, biu = (w.parts[0] for w in words)

        self.assertEqual(bold.style.bold, True)
        self.assertEqual(bold.style.italic, False)
        self.assertEqual(bold.style.underline, False)

        self.assertEqual(strong.style.bold, True)
        self.assertEqual(strong.style.italic, False)
        self.assertEqual(strong.style.underline, False)

        self.assertEqual(italic.style.bold, False)
        self.assertEqual(italic.style.italic, True)
        self.assertEqual(italic.style.underline, False)

        self.assertEqual(underline.style.bold, False)
        self.assertEqual(underline.style.italic, False)
        self.assertEqual(underline.style.underline, True)

        self.assertEqual(biu.style.bold, True)
        self.assertEqual(biu.style.italic, True)
        self.assertEqual(biu.style.underline, True)

    def test_chunking(self):
        p = self.parse(["<p>", "I", "’ve ", "I’ve</p>"])
        words = p.words
        self.assertEqual(len(words), 2)
        self.assertEqual(str(words[0]), 'I’ve')
        self.assertEqual(str(words[1]), 'I’ve')

    def test_nesting(self):
        p = self.parse(["<p>", "I<b>", "’<i>ve</i> ", "I</b>’ve</p>"])
        words = p.words
        self.assertEqual(len(words), 2)
        self.assertEqual(str(words[0]), 'I’ve')
        self.assertEqual(str(words[1]), 'I’ve')

    def test_br_tag(self):
        p = self.parse("<p>Break tag<br/>should close word.</p>")
        words = p.words
        self.assertEqual(len(words), 6)
        self.assertEqual(str(words[1]), 'tag')
        self.assertEqual(words[2], Break)
        self.assertEqual(str(words[3]), 'should')

    def test_nbsp_ignored(self):
        p = self.parse("<p>Non &nbsp; breaking space.</p>")
        words = p.words
        self.assertEqual(len(words), 3)
        self.assertEqual(str(words[0]), 'Non')
        self.assertEqual(str(words[1]), 'breaking')


class TestRendering(BaseTestCase):

    def test_wrap(self):
        p = self.parse(
            "<p>Some people don't like change, but you need to "
            "embrace change if the alternative is disaster.</p>"
        )
        self.assertEqual(p.wrap(100), (100, 84))

    def test_draw_merges_same_styled_words(self):
        s = Style.default()
        self.assertPDF(Paragraph([
            Word(s, 'hello'),
            Word(s, 'world').add(s, '!')
        ], s), [
            "BT",
            "1 0 0 1 0 0 Tm",
            "/F1 12 Tf 14 TL",
            "0 0 Td",
            "(hello world!) Tj T*",
            "ET"
        ])

    def test_draw_optimally_switches_fonts(self):
        # merge continous fragments of the same style
        # into a single Tj draw command
        # <p>hello <b>world</b>, systori<b>!</b></p>
        s = Style.default()
        self.assertPDF(Paragraph([
            Word(s, 'hello'),
            Word(s.set(bold=True), 'world').add(s, ','),
            Word(s, 'systori').add(s.set(bold=True), '!'),
        ], s), [
            "BT",
            "1 0 0 1 0 0 Tm",
            "/F1 12 Tf 14 TL",
            "0 0 Td",
            "(hello ) Tj",
            "/F2 12 Tf",
            "(world) Tj",
            "/F1 12 Tf",
            "(, systori) Tj",
            "/F2 12 Tf",
            "(!) Tj T*",
            "ET"
        ])
