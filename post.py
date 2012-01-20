import os, imp, doctest, datetime, re
from collections import OrderedDict, namedtuple
from util import slugify, render_to
import settings

import pygments_rest

RSTError = namedtuple('RSTError', 'filename line type message text')

metadata_attrs = ('date','title','tags','author','draft')

class DocTestPart(object):
    def __init__(self, example=None):
        self.examples = []
        if example:
            self.add(example)

    def add(self, example):
        example.source = re.split('\s*#\s*doctest\s*:',example.source)[0]
        self.examples.append(example)
    def __repr__(self):
        return '<DocTestPart>'+self.examples.__repr__()

    def get_rst(self):
        code = []
        for example in self.examples:
            source = '>>> '+'\n   ... '.join(example.source.strip().split('\n'))
            code.append(source)
            if getattr(example, 'last_got', None):
                code.append(example.last_got.strip().replace('\n','\n   '))
            elif example.want:
                code.append(example.want.strip().replace('\n','\n   '))

        ret = '.. sourcecode:: pycon\n\n   '+('\n   '.join(code))+'\n'
        return ret

class TextPart(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

    def get_rst(self):
        return self.text+'\n'

class CodePart(object):
    def __init__(self, code):
        self.code = code

    def add(self, code):
        self.code = '\n'.join((self.code, code))
    def __str__(self):
        return self.code
    def __repr__(self):
        return '<CodePart>'+self.code

    def get_rst(self):
        ret = '.. sourcecode:: python\n    :linenos:\n\n    '+self.code.replace('\n', '\n    ')+'\n'
        return ret

class Post(object):
    def __init__(self, module_path):
        self.module_path = module_path
        self.filename    = filename = os.path.basename(module_path)

        pdw_id = filename.split('_')[0].lstrip('0')
        try:
            self.id = int(pdw_id)
        except ValueError:
            raise ValueError('PDWs should start with a unique integer representing the PDW ID.'+str(file_path))
        
        module_name = filename.split('.')[0].lstrip('_01234567890')
        #print pdw_id, module_name

        imp_desc  = ('', 'r', imp.PY_SOURCE)
        with open(module_path) as module_file:
            self.module     = imp.load_module(module_name, module_file, module_path, imp_desc)
            module_file.seek(0)
            self.module_src = module_file.read()

        self.title    = self.module.title
        self.author   = self.module.author # TODO: settings.AUTHORS lookup
        self.tags     = getattr(self.module,'tags',())
        self.is_draft = getattr(self.module,'draft',False)
        self.date     = datetime.datetime(*self.module.date)
        self.slug     = slugify(unicode(self.title))

        self.parts    = get_parts(self.module_src)

        self.run_examples()

        # so much for laziness, gotta call this to get errors populated (TODO, fix)
        self._html = self._get_html()


    def run_examples(self):
        from doctest import DocTest, DocTestRunner
        examples = sum([part.examples for part in self.parts if isinstance(part, DocTestPart)],[])
        dt = DocTest(examples, self.module.__dict__, self.filename, None, None, None)
        dtr = DocTestRunner()

        def tmp_out(message_to_throw_away):
            return

        dtr.run(dt, out=tmp_out, clear_globs=False)

    @property
    def rst(self):
        rst = getattr(self, '_rst', None)
        if not rst:
            self._rst = rst = '\n'.join([part.get_rst() for part in self.parts])
        return rst

    @property
    def html(self):
        html = getattr(self, '_html', None)
        if not html:
            self._html = html = self._get_html()
        return html

    def _get_html(self, body_only=True):
        import sys
        import pygments_rest
        from docutils.core import Publisher
        from docutils.io import StringInput, StringOutput
        from cStringIO import StringIO
        
        settings = {'doctitle_xform'     : 1,
                    'pep_references'     : 1,
                    'rfc_references'     : 1,
                    'footnote_references': 'superscript',
                    'output_encoding'    : 'unicode',
                    'report_level'       : 2, # 2=show warnings, 3=show only errors, 5=off (docutils.utils
                    }

        post_rst = render_to('post_single.rst.mako', post=self)

        pub = Publisher(reader=None, 
                        parser=None, 
                        writer=None, 
                        settings=None,
                        source_class=StringInput,
                        destination_class=StringOutput)

        pub.set_components(reader_name='standalone',
                           parser_name='restructuredtext',
                           writer_name='html')
        pub.process_programmatic_settings(settings_spec=None,
                                          settings_overrides=settings,
                                          config_section=None)
        pub.set_source(post_rst,source_path=self.module_path)
        pub.set_destination(None, None)

        errors_io = StringIO()
        real_stderr = sys.stderr
        sys.stderr = errors_io
        try:
            html_full = pub.publish(enable_exit_status=False)
            html_body = ''.join(pub.writer.html_body)
        finally:
            sys.stderr = real_stderr
        errors = errors_io.getvalue()
        self._process_rest_errors(errors)

        errors_io.close()

        return html_body if body_only else html_full

    def _process_rest_errors(self, docutils_errors):
        errors = []
        docutils_err_list = docutils_errors.split('\n')
        for err in docutils_err_list:
            if err.strip() == '':
                continue
            try:
                fields   = err.split(':')
                filename = fields[0].strip()
                line     = fields[1].strip()
                
                type_message = fields[2].strip().split(' ')
                err_type = type_message[0]
                message  = ' '.join(type_message[1:])
                
                text     = ':'.join(fields[3:]).strip(' .')

                errors.append(RSTError(filename, line, err_type, message, text))
            except IndexError as ie:
                pass
        self.rst_errors = errors

def get_parts(string):
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
        if isinstance(node, Assign) and node.targets[0].id in metadata_attrs:
            continue
        elif isinstance(node, Expr) and isinstance(node.value, Str):
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
        else:
            last_line = 0
            for subnode in ast.walk(node):
                last_line = max(getattr(subnode,'lineno',0), last_line)
            code_str = '\n'.join(lines[lineno-1:last_line]).strip()
            if ret and isinstance(ret[-1], CodePart):
                ret[-1].add(code_str)
            else:
                ret.append(CodePart(code_str))

    return ret

