from unittest import TestCase

from bericht.html import *
from bericht.text import *
from bericht.style import *


class TestHtmlParagraphs(TestCase):

    def test_bold_italic(self):
        result = parse_html('<p><b>hello</b> <i>world</i></p>', BlockStyle.default())
        self.assertIsInstance(result[0], Paragraph)
        words = result[0].words
        self.assertEqual(len(words), 2)
        hello, world = (w.parts[0] for w in words)
        self.assertEqual(hello.style.bold, True)
        self.assertEqual(hello.style.italic, False)
        self.assertEqual(world.style.bold, False)
        self.assertEqual(world.style.italic, True)
