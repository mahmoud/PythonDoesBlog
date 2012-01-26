from collections import namedtuple

SOURCE_DIR     = '../PythonDoesWhat/'
SOURCE_EXCLUDE = ('pdw.py','__init__.py')

Author = namedtuple('Author', ('name', 'full_name', 'email'))
AUTHORS = {'Kurt': Author('Kurt', 'Kurt Rose', 'kurt@pythondoeswhat.com'),
           'Mahmoud': Author('Mahmoud', 'Mahmoud Hashemi', 'mahmoud@pythondoeswhat.com')
           }
POSTS_PER_PAGE = 5


OUTPUT_DIR    = './pub/'
TEMPLATE_DIRS = ['./templates/']

PYGMENTS_STYLE = "friendly"

DISQUS_SHORTNAME = 'pythondoeswhat'

ANALYTICS_CODE = """<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-28477666-1']);
  _gaq.push(['_setDomainName', 'pythondoeswhat.com']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>"""
