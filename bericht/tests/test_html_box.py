from bericht.tests.utils import BaseTestCase


class TestTextWrap(BaseTestCase):

    def get_box(self, content):
        return next(iter(self.parse(content)))

    def test_blank(self):
        box = self.get_box('<p>')
        self.assertEqual(box.children, [])
        box.wrap(None, 200)
        self.assertEqual(box.lines, [])

    def test_single_line(self):
        box = self.get_box('<p>hello <i>world</i>!')
        self.assertEqual(len(box.children), 3)
        box.wrap(None, 200)
        self.assertEqual(box.lines, [])
