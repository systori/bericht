from unittest import TestCase
from bericht.style import *


class TestCache(TestCase):

    def test_caching(self):
        block = BlockStyle.default()
        initial = TextStyle.from_block(block)
        bolded1 = initial.set(bold=True)
        bolded2 = initial.set(bold=True)
        self.assertEqual(bolded1, bolded2)
        self.assertIs(bolded1, bolded2)
