import os, imp, doctest, datetime
from collections import OrderedDict, namedtuple
import settings

source_dir = settings.SOURCE_DIR
posts      = OrderedDict()

class Post(object):
    def __init__(self, module_path):
        #print pdw_id, module.__name__
        file_name = os.path.basename(module_path)

        pdw_id = file_name.split('_')[0].lstrip('0')
        try:
            self.id = int(pdw_id)
        except ValueError:
            raise ValueError('PDWs should start with a unique integer representing the PDW ID.'+str(file_path))
        
        module_name = file_name.split('.')[0].lstrip('_01234567890')
        imp_desc  = ('', 'r', imp.PY_SOURCE)
        with open(module_path) as module_file:
            self.module     = imp.load_module(module_name, module_file, module_path, imp_desc)
            module_file.seek(0)
            self.module_src = module_file.read()

        self.title  = self.module.title
        self.author = self.module.author # TODO: settings.AUTHORS lookup
        self.tags   = getattr(self.module,'tags',())
        self.date   = datetime.datetime(*self.module.date)

        self.components = get_components(self.module_src)

def generate():
    post_list = []
    for file_path in os.listdir(settings.SOURCE_DIR):
        if not file_path.endswith('.py') or file_path in settings.SOURCE_EXCLUDE:
            continue

        full_path = os.path.join(source_dir, file_path)
        try:
            post_list.append(Post(full_path))
        except Exception as e:
            print 'Error creating Post from '+str(full_path)+':'+str(e)
            continue

    # import pdb;pdb.set_trace()

# TODO: automatic linking to other PDWs via syntax PDWxxx where xxx is an integer ID


class DocTestPart(object):
    def __init__(self, example):
        self.examples = [example]
    def add(self, example):
        self.examples.append(example)
    def __repr__(self):
        return '<DocTestPart>'+self.examples.__repr__()

class TextPart(str):
    def __repr__(self):
        return 'TextPart: '+str.__repr__(self)
class CodePart(str):
    def __repr__(self):
        return 'CodePart: '+str.__repr__(self)

metadata_attrs = ('date','title','tags','author')
def get_components(string):
    ret = []
    import ast
    from ast import Expr, Str, Assign
    from doctest import DocTestParser,Example
    dtp = DocTestParser()
    lines = string.split("\n")
    m_ast = ast.parse(string)
    str_linestarts = [ x.lineno for x in m_ast.body if isinstance(x, Expr) and isinstance(x.value, Str)]
    for i, node in enumerate(m_ast.body):
        lineno = node.lineno
        if isinstance(node, Expr) and isinstance(node.value, Str):
            for s in dtp.parse(node.value.s):
                if isinstance(s, Example):
                    if ret and isinstance(ret[-1], DocTestPart):
                        ret[-1].add(s)
                    else:
                        ret.append(DocTestPart(s))
                elif len(s.strip()) > 0:
                    ret.append(TextPart(s.strip()))
                else:
                    continue
        elif isinstance(node, Assign) and node.targets[0].id in metadata_attrs:
            continue
        else:
            last_line = 0
            for subnode in ast.walk(node):
                last_line = max(getattr(subnode,'lineno',0), last_line)
            code_str = '\n'.join(lines[lineno-1:last_line]).strip()
            if ret and isinstance(ret[-1], CodePart):
                ret[-1] = CodePart('\n'.join((ret[-1],code_str)))
            else:
                ret.append(CodePart(code_str))

    return ret

if __name__ == '__main__':
    generate()
