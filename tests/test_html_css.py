from unittest import TestCase, skip
from tinycss2 import parse_one_rule

from bericht.html.css import parse_selectors
from utils import BaseTestCase


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


class TestMatch(BaseTestCase):

    def test_class_tag_id_selectors(self):
        nodes = self.parse("""
            <p>initial</p>
            <p class="bolded">bolded</p>
            <p class="big bolded">big bolded</p>
            <p id="withid">small</p>
        """, """
            #withid, .bolded { font-size: 14pt; }
            .bolded { font-weight: bold; }
            p.big { font-size: 16pt; }
        """)
        initial, bolded, big, withid = nodes
        self.assertEqual(initial.style.font_size, 12)
        self.assertEqual(initial.style.font_weight, '')
        self.assertEqual(bolded.style.font_size, 14)
        self.assertEqual(bolded.style.font_weight, 'bold')
        self.assertEqual(big.style.font_size, 16)
        self.assertEqual(big.style.font_weight, 'bold')
        self.assertEqual(withid.style.font_size, 14)
        self.assertEqual(withid.style.font_weight, '')

    def test_combinators(self):
        nodes = list(self.parse("""
            <p><b>text</b></p>
            <div><b>text</b></div>
            <div><p><b>text</b></p></div>
        """, """
            b { font-size: 14pt; }
            div b { font-size: 16pt; }
            div > b { color: green; }
        """))
        p_b = nodes[0].children[0]
        div_b = nodes[1].children[0]
        div_p_b = nodes[2].children[0].children[0]
        self.assertEqual(p_b.style.font_size, 14)
        self.assertEqual(div_b.style.font_size, 16)
        #self.assertEqual(div_p_b.style.font_size, 16)

    def test_odd_even_row_background(self):
        nodes = list(self.parse("""
        <table>
          <tbody>
            <tr><td>odd row</td></tr>
            <tr><td>even row</td></tr>
            <tr><td>odd 2 row</td></tr>
            <tr><td>even 2 row</td></tr>
          </tbody> 
        </table>
        """, """
        table > tbody > tr:nth-child(even) {
          background-color: green;
        }
        """))
        odd, even, odd2, even2 = nodes
        self.assertIsNone(odd.style.background_color)
        self.assertIsNotNone(even.style.background_color)
        self.assertIsNone(odd2.style.background_color)
        self.assertIsNotNone(even2.style.background_color)
