from tinycss2 import parse_stylesheet, parse_declaration_list, parse_one_component_value, ast
from bericht.style import Style

__all__ = ('CSS',)


class Combinator:

    DESCENDANT = 1          # E F    an F element descendant of an E element
    CHILD = 2               # E > F  an F element child of an E element
    NEXT_SIBLING = 3        # E + F  an F element immediately preceded by an E element
    SUBSEQUENT_SIBLING = 4  # E ~ F  an F element preceded by an E element

    __slots__ = ('type', 'simple_selectors')

    def __init__(self):
        self.type = None
        self.simple_selectors = []

    def select_tag(self, tag):
        return lambda node: tag == node.tag

    def select_id(self, node_id):
        return lambda node: node_id == node.id

    def select_class(self, name):
        return lambda node: name in node.classes

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
        return True


class Declarations:

    def __init__(self, content):
        self.content = content
        self.attrs = {}
        for declaration in parse_declaration_list(content, skip_comments=True, skip_whitespace=True):
            value = parse_one_component_value(declaration.value, skip_comments=True)
            self.attrs[declaration.name.replace('-', '_')] = value.value

    def apply(self, node):
        if node.style:
            node.style = node.style.set(**self.attrs)
        else:
            parent = Style.default() if node.parent is None else node.parent.style
            node.style = parent.set(**self.attrs)


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
            if token in ('.', '#', ':'):
                if not prefix:
                    prefix = token.value
                else:
                    prefix += token.value
            elif isinstance(token, ast.IdentToken):
                if prefix is None:
                    combinator.add(combinator.select_tag, token.value)
                elif prefix == '.':
                    combinator.add(combinator.select_class, token.value)
                elif prefix == '#':
                    combinator.add(combinator.select_id, token.value)
                else:
                    raise RuntimeError
                prefix = None
            else:
                raise RuntimeError

    selectors.append(Selector(combinators))

    return selectors


class CSS:

    def __init__(self, src):
        self.src = src
        self.rules = []
        for rule in parse_stylesheet(src, skip_comments=True, skip_whitespace=True):
            if not isinstance(rule, ast.QualifiedRule):
                continue
            self.rules.append(
                (parse_selectors(rule.prelude), Declarations(rule.content))
            )

    def apply(self, node):
        for selectors, declarations in self.rules:
            for selector in selectors:
                if selector.matches(node):
                    declarations.apply(node)
