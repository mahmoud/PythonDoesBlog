<%!
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

import settings
%>

<%def name="highlight(code, lang='python')">
<%
lexer = get_lexer_by_name(lang.strip('"'), stripall=True) #"
formatter = HtmlFormatter(linenos=True, cssclass=settings.PYGMENTS_STYLE)
result = highlight(code, lexer, formatter)
%>
${result}
</%def>

<%def name="highlight_repl(code)">
<%
lexer = get_lexer_by_name('pycon', stripall=True)
formatter = HtmlFormatter(nowrap=True, linenos=False, cssclass=settings.PYGMENTS_STYLE)
result = highlight(code, lexer, formatter)
%>
${result}
</%def>
