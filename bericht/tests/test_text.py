from unittest import TestCase

from reportlab.pdfgen.canvas import Canvas

from bericht.text import *
from bericht.style import Style


class TestMetrics(TestCase):

    def test_wrap(self):
        text = Paragraph.from_string(
            "Some people don't like change, but you need to "
            "embrace change if the alternative is disaster."
        )
        self.assertEqual(text.wrap(20, 10), (20, 238))


class TestDraw(TestCase):

    def setUp(self):
        self.style = Style.default()

    def draw(self, p):
        p.wrap(200, 100)
        canvas = Canvas(None)
        p.canv = canvas
        p.draw()
        return canvas._code[0]

    def assertPDF(self, input, output):
        self.assertEqual(self.draw(input), ' '.join(output))

    def test_same_style_merged(self):
        self.assertPDF(Paragraph([
            Word(self.style, 'hello'),
            Word(self.style, 'world').add(self.style, '!')
        ], self.style), [
            "BT",
            "1 0 0 1 0 0 Tm",
            "/F1 12 Tf 14 TL",
            "(hello world!) Tj T*",
            "ET"
        ])

    def test_optimal_draw_calls(self):
        # merge continous fragments of the same style
        # into a single Tj draw command
        # <p>hello <b>world</b>, systori<b>!</b></p>
        self.assertPDF(Paragraph([
            Word(self.style, 'hello'),
            Word(self.style.set(bold=True), 'world').add(self.style, ','),
            Word(self.style, 'systori').add(self.style.set(bold=True), '!'),
        ], self.style), [
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
