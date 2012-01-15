from collections import namedtuple

SOURCE_DIR     = '../PythonDoesWhat/'
SOURCE_EXCLUDE = ('pdw.py','__init__.py')

Author = namedtuple('Author', ('name', 'full_name', 'email'))
AUTHORS = {'Kurt': Author('Kurt', 'Kurt Rose', 'kurt@pythondoeswhat.com'),
           'Mahmoud': Author('Mahmoud', 'Mahmoud Hashemi', 'mahmoud@pythondoeswhat.com')
           }


