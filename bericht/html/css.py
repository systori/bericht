from os.path import dirname, join
from tinycss2 import (
    parse_stylesheet, parse_declaration_list,
    ast, nth, color3
)

from bericht.html.style import Style, BorderCollapse, BorderStyle
from bericht.html.box import Box

__all__ = ('CSS',)

inch = 72.0
cm = inch / 2.54
mm = cm * 0.1

units = {
    'px': 1,
    'pt': 1,
    'mm': mm,
    'cm': cm,
    'inch': inch
}


def convert(value):
    if isinstance(value, ast.NumberToken):
        return value.value
    if value.unit in units:
        return value.value * units[value.unit]
    raise NotImplementedError(
        'Dimension unit "{}" is not implemented yet.'.format(value.unit)
    )


class Combinator:

    DESCENDANT = 1          # E F    an F element descendant of an E element
    CHILD = 2               # E > F  an F element child of an E element
    NEXT_SIBLING = 3        # E + F  an F element immediately preceded by an E element
    SUBSEQUENT_SIBLING = 4  # E ~ F  an F element preceded by an E element

    __slots__ = ('type', 'simple_selectors')

    def __init__(self):
        self.type = None
        self.simple_selectors = []

    @staticmethod
    def select_tag(tag):
        return lambda node: tag == node.tag

    @staticmethod
    def select_id(node_id):
        return lambda node: node_id == node.id

    @staticmethod
    def select_class(name):
        return lambda node: name in node.classes

    @staticmethod
    def select_attributes(attrs):
        assert all(isinstance(attr, ast.IdentToken) for attr in attrs)

        def attr_test(node):
            for attr in attrs:
                if attr.lower_value not in node.attrs:
                    return False
            return True

        return attr_test

    @staticmethod
    def select_position(a_b):
        a, b = a_b

        def position_test(node):
            if a == 0:  # nth-child(0n+b)
                return node.position == b
            else:  # nth-child(an+b)
                return node.position >= b and (node.position-b) % a == 0

        return position_test

    @staticmethod
    def select_last_child(last_child):
        def is_last_child(node):
            return last_child == node.last
        return is_last_child

    def add(self, selector, value, negate=False):
        matcher = selector(value)
        if negate:
            self.simple_selectors.append(lambda node: not matcher(node))
        else:
            self.simple_selectors.append(matcher)

    def matches(self, node):
        for simple_selector in self.simple_selectors:
            if not simple_selector(node):
                return False
        return True


class Selector:

    __slots__ = ('combinators',)

    def __init__(self, combinators):
        self.combinators = combinators

    def matches(self, node):
        for combinator in reversed(self.combinators):
            if not combinator.matches(node):
                return False
            node = node.parent
        return True


class Declarations:

    def __init__(self, content):
        self.content = content
        self.attrs = {}
        for declaration in parse_declaration_list(content, skip_comments=True, skip_whitespace=True):
            if isinstance(declaration, ast.AtRule):
                if declaration.at_keyword == 'bottom-right':
                    at_dec = Declarations(declaration.content)
                    self.attrs['page_bottom_right_content'] = at_dec.attrs['content']
                else:
                    raise NotImplementedError
            elif declaration.name == 'content':
                self.attrs[declaration.name.replace('-', '_')] = parse_content_value(declaration.value)
            else:
                attr = declaration.name.replace('-', '_')
                value_parts = parse_value_parts(declaration.value)
                if declaration.name in ('color', 'background-color'):
                    self.attrs[attr] = color3.parse_color(value_parts[0])
                elif declaration.name in ('margin', 'padding'):
                    apply_box_values(
                        self.attrs, declaration.name+'_{}',
                        list(map(convert, value_parts))
                    )
                elif declaration.name == 'border-color':
                    apply_box_values(self.attrs, 'border_{}_color', list(map(color3.parse_color, value_parts)))
                elif declaration.name == 'border-width':
                    apply_box_values(self.attrs, 'border_{}_width', list(map(convert, value_parts)))
                elif declaration.name == 'border-collapse':
                    self.attrs[attr] = getattr(BorderCollapse, value_parts[0].value)
                elif declaration.name == 'border-style':
                    apply_box_values(self.attrs, 'border_{}_style',
                                     [getattr(BorderStyle, v.value) for v in value_parts])
                elif declaration.name == 'border-spacing':
                    if len(value_parts) == 1:
                        self.attrs['border_spacing_horizontal'] = value_parts[0].value
                        self.attrs['border_spacing_vertical'] = value_parts[0].value
                    else:
                        (self.attrs['border_spacing_horizontal'],
                         self.attrs['border_spacing_vertical']) = value_parts
                elif declaration.name.startswith('border-'):
                    if declaration.name.endswith('-style'):
                        self.attrs[attr] = getattr(BorderStyle, value_parts[0].value)
                    elif declaration.name.endswith('-color'):
                        self.attrs[attr] = color3.parse_color(value_parts[0])
                    elif declaration.name.endswith('-width'):
                        self.attrs[attr] = convert(value_parts[0])
                elif isinstance(value_parts[0], ast.DimensionToken):
                    self.attrs[attr] = convert(value_parts[0])
                else:
                    self.attrs[attr] = value_parts[0].value

    def apply(self, node):
        if node.style:
            node.style = node.style.set(**self.attrs)
        else:
            parent = Style.default() if node.parent is None else node.parent.style
            node.style = parent.set(**self.attrs)


def apply_box_values(attrs, attr, values):
    if len(values) == 1:
        attrs[attr.format('top')] = values[0]
        attrs[attr.format('right')] = values[0]
        attrs[attr.format('bottom')] = values[0]
        attrs[attr.format('left')] = values[0]
    elif len(values) == 2:
        attrs[attr.format('top')] = values[0]
        attrs[attr.format('right')] = values[1]
        attrs[attr.format('bottom')] = values[0]
        attrs[attr.format('left')] = values[1]
    elif len(values) == 3:
        attrs[attr.format('top')] = values[0]
        attrs[attr.format('right')] = values[1]
        attrs[attr.format('bottom')] = values[2]
        attrs[attr.format('left')] = values[1]
    else:
        (attrs[attr.format('top')],
         attrs[attr.format('right')],
         attrs[attr.format('bottom')],
         attrs[attr.format('left')]) = values


def parse_value_parts(tokens):
    return list(filter(lambda token: token.type not in ('whitespace', 'comment'), tokens))


def parse_content_value(value):
    parts = []
    for part in value:
        if isinstance(part, ast.StringToken):
            parts.append(part.value)
        elif isinstance(part, ast.FunctionBlock):
            if part.lower_name == 'counter' and part.arguments[0].lower_value == 'page':
                parts.append(lambda page: page.page_number)
            else:
                raise NotImplementedError
        elif isinstance(part, ast.WhitespaceToken):
            pass
        else:
            raise NotImplementedError

    return lambda page: ''.join(
        [p if isinstance(p, str) else str(p(page)) for p in parts]
    )


def parse_selectors(prelude):
    selectors = []
    combinator = None
    combinators = []
    prefix = None

    for token in prelude:
        if isinstance(token, ast.WhitespaceToken):
            combinator = None
        elif token == ',':
            selectors.append(Selector(combinators))
            combinator = None
            combinators = []
        elif token == '>':
            combinators[-1].type = Combinator.CHILD
            combinator = None
        elif token == '+':
            combinators[-1].type = Combinator.NEXT_SIBLING
            combinator = None
        elif token == '~':
            combinators[-1].type = Combinator.SUBSEQUENT_SIBLING
            combinator = None
        else:
            if not combinator:
                combinator = Combinator()
                combinators.append(combinator)
            if token in ('.', ':'):
                if not prefix:
                    prefix = token.value
                else:
                    prefix += token.value
            elif isinstance(token, ast.IdentToken):
                if prefix is None:
                    combinator.add(combinator.select_tag, token.value)
                elif prefix == '.':
                    combinator.add(combinator.select_class, token.value)
                elif prefix == ':':
                    if token.value == 'first':
                        combinator.add(combinator.select_position, (0, 1))
                    elif token.value in ('last', 'last-child'):
                        combinator.add(combinator.select_last_child, True)
                    else:
                        raise NotImplementedError
                else:
                    raise NotImplementedError
                prefix = None
            elif isinstance(token, ast.HashToken):
                prefix = None
                combinator.add(combinator.select_id, token.value)
            elif isinstance(token, ast.FunctionBlock):
                prefix = None
                if token.name == 'nth-child':
                    combinator.add(combinator.select_position, nth.parse_nth(token.arguments))
                elif token.name == 'nth-of-type':
                    raise NotImplementedError
            elif isinstance(token, ast.SquareBracketsBlock):
                prefix = None
                combinator.add(combinator.select_attributes, token.content)
            else:
                raise NotImplementedError

    selectors.append(Selector(combinators))

    return selectors


class CSS:

    def __init__(self, src):
        self.src = src
        self.rules = []
        with open(join(dirname(__file__), 'html.css'), 'r') as html_css:
            self.parse(html_css.read())
        self.parse(src)

    def parse(self, src):
        for rule in parse_stylesheet(src, skip_comments=True, skip_whitespace=True):
            if isinstance(rule, ast.AtRule) and rule.at_keyword == 'page':
                selectors = parse_selectors(rule.prelude)
                for selector in selectors:
                    for combinator in selector.combinators:
                        combinator.add(combinator.select_tag, '@page')
                    if not selector.combinators:
                        combinator = Combinator()
                        combinator.add(combinator.select_tag, '@page')
                        selector.combinators.append(combinator)
                self.rules.append(
                    (selectors, Declarations(rule.content))
                )
            elif isinstance(rule, ast.QualifiedRule):
                self.rules.append(
                    (parse_selectors(rule.prelude), Declarations(rule.content))
                )

    def apply(self, node):
        for selectors, declarations in self.rules:
            for selector in selectors:
                if selector.matches(node):
                    declarations.apply(node)

    def apply_recursively(self, node):
        self.apply(node)
        for child in node.children:
            if isinstance(child, Box):
                self.apply_recursively(child)
