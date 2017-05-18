from unittest import TestCase

from reportlab.pdfgen.canvas import Canvas

from bericht.text import *
from bericht.style import Style


class BasePDFTestCase(TestCase):

    def draw(self, p):
        canvas = Canvas(None)
        p.wrapOn(canvas, 200, 100)
        p.canv = canvas
        p.draw()
        return canvas._code[0]

    def assertPDF(self, input, output):
        self.assertEqual(self.draw(input), ' '.join(output))


class TestText(BasePDFTestCase):

    def test_wrap(self):
        text = static(
            "Some people don't like change, but you need to "
            "embrace change if the alternative is disaster."
        )
        self.assertEqual(text.width, 494.55600000000004)
        self.assertEqual(text.min_content_width, 494.55600000000004)
        self.assertEqual(text.height, 14)
        self.assertEqual(text.wrapOn(None, 20, 10), (494.55600000000004, 14))

    def test_draw(self):
        self.assertPDF(static('hello world!'), [
            "BT",
            "1 0 0 1 0 0 Tm",
            "/F1 12 Tf",
            "(hello world!) Tj",
            "ET"
        ])


class TestParagraph(BasePDFTestCase):

    def test_wrap(self):
        text = para(
            "Some people don't like change, but you need to "
            "embrace change if the alternative is disaster."
        )
        self.assertEqual(text.wrap(100), (100, 84))

    def test_draw_merges_same_styled_words(self):
        s = Style.default()
        self.assertPDF(Paragraph([
            Word(s, 'hello'),
            Word(s, 'world').add(s, '!')
        ], s), [
            "BT",
            "1 0 0 1 0 0 Tm",
            "/F1 12 Tf 14 TL",
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
            "(hello ) Tj",
            "/F2 12 Tf",
            "(world) Tj",
            "/F1 12 Tf",
            "(, systori) Tj",
            "/F2 12 Tf",
            "(!) Tj T*",
            "ET"
        ])
