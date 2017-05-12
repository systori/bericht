from unittest import TestCase
from bericht.style import *

S = Style.default()


class TestCache(TestCase):

    def test_caching(self):
        bolded1 = S.set(bold=True)
        bolded2 = S.set(bold=True)
        self.assertEqual(bolded1, bolded2)
        self.assertIs(bolded1, bolded2)


class TestValidation(TestCase):

    def test_vertical_align(self):
        self.assertEqual(S.vertical_align, VerticalAlign.top)
        vert = S.set(vertical_align=VerticalAlign.bottom)
        self.assertEqual(vert.vertical_align, VerticalAlign.bottom)
        with self.assertRaises(AssertionError):
            S.set(vertical_align="foo")

    def test_page_break_inside(self):
        self.assertEqual(S.page_break_inside, True)
        pb = S.set(page_break_inside=False)
        self.assertEqual(pb.page_break_inside, False)
        with self.assertRaises(AssertionError):
            S.set(page_break_inside="foo")
