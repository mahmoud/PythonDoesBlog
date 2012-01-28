from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter


from settings import PYGMENTS_STYLE

DEFAULT = HtmlFormatter(cssclass='code '+PYGMENTS_STYLE)
OPTIONS = ('linenos', 'noclasses')

class Pygments(Directive):
    """ Source code syntax hightlighting."""

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(o, directives.flag) for o in OPTIONS])

    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        
        formatter = DEFAULT
        if self.options:
            options = dict((o, o in self.options) for o in OPTIONS)
            if not options.get('noclasses'):
                options['cssclass'] = 'code '+PYGMENTS_STYLE

            formatter = HtmlFormatter(**options)

        parsed = highlight(u'\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]

directives.register_directive('sourcecode', Pygments)
