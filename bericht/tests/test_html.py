from unittest import TestCase

from bericht.html import *
from bericht.text import *
from bericht.style import *


class TestParagraphCollector(TestCase):

    def test_bold_italic_underline(self):

        p = parse_html(
            '<p><b>hello</b> <i>world</i>, <u>bericht</u>! '
            '<strong>strong</strong> <b><i><u>biu</u></i></b></p>',
            BlockStyle.default()
        )

        self.assertIsInstance(p[0], Paragraph)

        words = p[0].words
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

    def test_lxml_chunking_not_result_in_extraneous_space(self):
        # lxml parser calls EventTarget.data() twice for this string:
        # 1. data("I")
        # 2. data("’ve I’ve")
        # make sure that the end result is only two words
        p = parse_html("<p>I’ve I’ve</p>", BlockStyle.default())
        words = p[0].words
        self.assertEqual(len(words), 2)
        self.assertEqual(str(words[0]), 'I’ve')
        self.assertEqual(str(words[1]), 'I’ve')
