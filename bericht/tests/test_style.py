from unittest import TestCase
from bericht.style import *

block = BlockStyle.default()


class TestCache(TestCase):

    def test_caching(self):
        initial = TextStyle.from_style(block)
        bolded1 = initial.set(bold=True)
        bolded2 = initial.set(bold=True)
        self.assertEqual(bolded1, bolded2)
        self.assertIs(bolded1, bolded2)


class TestCellStyleValidation(TestCase):

    def test_vertical_align(self):
        style = CellStyle.from_style(block)
        self.assertEqual(style.vertical_align, VerticalAlign.top)
        style = style.set(vertical_align=VerticalAlign.bottom)
        self.assertEqual(style.vertical_align, VerticalAlign.bottom)
        with self.assertRaises(AssertionError):
            style.set(vertical_align="foo")


class TestRowStyleValidation(TestCase):

    def test_page_break_inside(self):
        style = RowStyle.from_style(block)
        self.assertEqual(style.page_break_inside, True)
        style = style.set(page_break_inside=False)
        self.assertEqual(style.page_break_inside, False)
        with self.assertRaises(AssertionError):
            style.set(page_break_inside="foo")
