import os.path
from utils import BaseTestCase
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bericht.pdf import PDFDocument

rl_config.TTFSearchPath = [os.path.join(os.path.dirname(__file__), 'fonts')]

font_name = "Ubuntu"
for font_face in ['Regular', 'Italic', 'Bold', 'BoldItalic']:
    font_family_member = '{}-{}'.format(font_name, font_face)
    pdfmetrics.registerFont(TTFont(font_family_member, font_family_member+'.ttf'))

pdfmetrics.registerFontFamily(
    font_name,
    normal='{}-Regular'.format(font_name),
    bold='{}-Bold'.format(font_name),
    italic='{}-Italic'.format(font_name),
    boldItalic='{}-BoldItalic'.format(font_name)
)


class TestFont(BaseTestCase):

    def render(self, html, css=None):
        parser = self.parse(html, css)
        p = next(iter(parser))
        doc = PDFDocument(parser.css)
        page = doc.add_page()
        p.wrap(page, page.available_width)
        p.draw(page, page.x, page.y)
        for _ in doc.header():
            pass
        for _ in page.read():
            pass
        for _ in doc.footer():
            pass

    def test_uninitialized_font_regression_helvetica(self):
        self.render("<table><tr><td>some text</td><td>&#931;</td></tr></table>")

    def test_uninitialized_font_regression_ubuntu(self):
        self.render("<table><tr><td>some text</td><td>&#931;</td></tr></table>",
                    "p { font-family: Ubuntu; }")
