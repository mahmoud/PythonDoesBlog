from collections import namedtuple

BLOG_TITLE = 'Python Does What'
BLOG_DESCRIPTION = 'Python idiosyncrasies and funtimes.'
BLOG_URL = 'http://www.pythondoeswhat.com/'

SOURCE_DIR     = '../PythonDoesWhat/'
SOURCE_EXCLUDE = ('pdw.py','__init__.py')
OUTPUT_DIR     = './pub/'
REMOTE_DIR     = 'makuro@pythondoeswhat.com:/home/makuro/pythondoeswhat.com'

Author = namedtuple('Author', ('name', 'full_name', 'email'))
AUTHORS = {'Kurt': Author('Kurt', 'Kurt Rose', 'kurt@pythondoeswhat.com'),
           'Mahmoud': Author('Mahmoud', 'Mahmoud Hashemi', 'mahmoud@pythondoeswhat.com')
           }
POSTS_PER_PAGE = 5

INTERNAL_ID   = 'pdw_id'
INTERNAL_NAME = 'PDW'

TEMPLATE_DIRS = ['./templates/']

SERVER_PORT = 7777

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


def get(name, default=None):
    return globals().get(name, default)
