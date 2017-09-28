from unittest import skip
from utils import BaseTestCase


class TestWordParsing(BaseTestCase):

    def get_box(self, content):
        return next(iter(self.parse(content)))

    def get_words(self, content):
        return list(map(str, self.get_box(content).boxes))

    def test_blank(self):
        self.assertEqual(self.get_words('<p>'), [])

    def test_plain_words(self):
        words = self.get_words('<p>hello world, bericht!')
        self.assertEqual(words, ['hello', 'world,', 'bericht!'])

    @skip
    def test_styled_words(self):
        words = self.get_words('<p>hello <i>world<b>,</b></i> <b>bericht</b><i>!</i>')
        self.assertEqual(words, ['hello', 'world,', 'bericht!'])


class TestWordWrapping(BaseTestCase):

    def get_box(self, content):
        return next(iter(self.parse(content)))

    def get_lines(self, box):
        return [list(map(str, line.words)) for line in box.lines]

    def test_blank(self):
        box = self.get_box('<p>')
        box.wrap(None, 200)
        self.assertEqual(box.lines, [])

    @skip
    def test_wrap_styled_words(self):
        box = self.get_box('<p>hello <i>world<b>,</b></i> <b>bericht</b><i>!</i>')
        box.wrap(None, 125)
        self.assertEqual(self.get_lines(box), [['hello', 'world,', 'bericht!']])
        box.wrap(None, 75)
        self.assertEqual(self.get_lines(box), [['hello', 'world,'], ['bericht!']])
        box.wrap(None, 50)
        self.assertEqual(self.get_lines(box), [['hello'], ['world,'], ['bericht!']])
