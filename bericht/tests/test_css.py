from unittest import TestCase

from bericht.css import CSS
from tinycss2 import parse_one_rule

from bericht.html import parse_html
from bericht.html.css import parse_selectors


class TestSelectorParsing(TestCase):

    def tokens(self, selector):
        return parse_one_rule(selector+'{}', skip_comments=True).prelude

    def parse(self, selector):
        return parse_selectors(self.tokens(selector))

    def assert_selector(self, tag, selectors=1, combinators=1, simple=1):
        sel = self.parse(tag)
        self.assertEqual(len(sel), selectors)
        self.assertEqual(len(sel[0].combinators), combinators)
        comb = sel[0].combinators[0]
        self.assertEqual(len(comb.simple_selectors), simple)

    def test_simple_tag(self):
        self.assert_selector(' p ')
        self.assert_selector('p ')
        self.assert_selector(' p')

    def test_multiple_selectors(self):
        self.assert_selector('p,b ', 2)
        self.assert_selector('p, b ', 2)
        self.assert_selector('p, b', 2)
        self.assert_selector('p,b', 2)

    def test_multiple_combinators(self):
        self.assert_selector('p b', 1, 2)
        self.assert_selector(' p  b ', 1, 2)
        self.assert_selector(' p >b ', 1, 2)
        self.assert_selector('p>b.foo', 1, 2)
        self.assert_selector('p>b>foo', 1, 3)
        self.assert_selector('p+b~foo', 1, 3)


class TestMatch(TestCase):

    def test_matching(self):
        css = CSS("""
            #withid, .bolded { font-size: 14pt; }
            .bolded { font-weight:bold; }
            p.big { font-size: 16pt; }
        """)
        nodes = parse_html("""
            <p>initial</p>
            <p class="bolded">bolded</p>
            <p class="big bolded">big bolded</p>
            <p id="withid">small</p>
        """)
        for node in nodes:
            css.apply(node)
        initial, bolded, big, withid = nodes
        self.assertEqual(initial.style.font_size, 12)
        self.assertEqual(initial.style.font_weight, '')
        self.assertEqual(bolded.style.font_size, 14)
        self.assertEqual(bolded.style.font_weight, 'bold')
        self.assertEqual(big.style.font_size, 16)
        self.assertEqual(big.style.font_weight, 'bold')
        self.assertEqual(withid.style.font_size, 1)
        self.assertEqual(withid.style.font_weight, '')
