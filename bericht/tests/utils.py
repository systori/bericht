from unittest import TestCase
from bericht.html import HTMLParser, CSS


def parse_html(html, css=None):
    return HTMLParser(
        lambda: iter(html if isinstance(html, list) else [html]),
        css if isinstance(css, CSS) else CSS(css or '')
    )


class BaseTestCase(TestCase):

    @staticmethod
    def parse(html, css=None):
        return parse_html(html, css)
