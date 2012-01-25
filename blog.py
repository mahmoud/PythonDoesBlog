import os, imp, doctest, datetime
from collections import OrderedDict, defaultdict, namedtuple

import settings
from settings import SOURCE_DIR, SOURCE_EXCLUDE, OUTPUT_DIR

from post import Post
from util import slugify, requires_pub_dir, render_to

class Blog(object):
    """
    Simply represents a collection of blog posts.
    """

    def __init__(self, src_path, exclude=() ):
        post_list = []
        
        for file_path in os.listdir(src_path):
            if not file_path.endswith('.py') or file_path in SOURCE_EXCLUDE:
                # TODO convert to regex matching
                continue
            full_path = os.path.join(src_path, file_path)
            try:
                post = Post(full_path)
                post_list.append(post)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print 'Error creating Post from '+str(full_path)+':'+str(e)
                continue

        self.posts = OrderedDict((p.id, p) for p in sorted(post_list, key=lambda p: p.date))

        self._check_monotonic()
        self._resolve_links()
        
        for post_id, post in self.posts.items():
            post.bake()
            for error in post.rst_errors:
                print 'Error in',post.filename,'on line',str(error.line)+': ',error.message,
                if error.text: print '('+error.text+')'

    @property
    def tag_dict(self):
        tag_dict = defaultdict(list)
        for id, post in self.posts.items():
            for tag in post.tags:
                tag_dict[tag].append(post)
        return tag_dict

    def _resolve_links(self):
        import re
        from itertools import chain

        def repl_link(match):
            pdw_id = int(match.group('pdw_id'))
            post = self.posts.get(pdw_id)
            if post:
                return '`' + match.group(0) + ' </posts/'+self.posts[pdw_id].slug+'.html>`_'
            else:
                return match.group(0)

        intlink = re.compile('(PDW[-|\s]*?(?P<pdw_id>\d+))')

        for text_part in chain.from_iterable(p.text_parts for p in self.posts.values()):
            text_part.text = intlink.sub(repl_link, text_part.text)

    def _check_monotonic(self):
        monotonic = True
        cur_max_id = 0
        for (pid, post) in self.posts.items():
            if cur_max_id > pid:
                print 'Warning:',cur_max_id,'appears to be out of order (publish date is before',pid,').'
                monotonic = False
            else:
                cur_max_id = pid
        return monotonic

    def render(self):
        self.render_posts()
        self.render_tag_pages()
        self.render_css()

    @requires_pub_dir
    def render_posts(self):
        with open(os.path.join(OUTPUT_DIR,'post_list.html'),'w') as pl_file:
            pl_file.write(render_to('post_list.html', posts=self.posts.values()))

        for pid, post in self.posts.items():
            with open(os.path.join(OUTPUT_DIR, 'posts', post.slug+'.html'), 'w') as p_html:
                p_html.write(render_to('post_single.html', post=post))
            with open(os.path.join(OUTPUT_DIR, 'posts', post.slug+'.rst'), 'w') as p_rst:
                p_rst.write(render_to('post_single.rst.mako', post=post))

    @requires_pub_dir
    def render_tag_pages(self):
        tag_dict = self.tag_dict
        for tag, posts in tag_dict.items():
            tag_slug = slugify(unicode(tag))
            with open(os.path.join(OUTPUT_DIR, 'tags', tag_slug+'.html'), 'w') as t_file:
                t_file.write(render_to('post_list.html', posts=posts))

        with open(os.path.join(OUTPUT_DIR, 'tags', 'tag_cloud.html'), 'w') as t_file:
            t_file.write(render_to('tag_cloud.html', tag_dict=tag_dict))

    @requires_pub_dir
    def render_css(self):
        from settings import PYGMENTS_STYLE
        from pygments.formatters import HtmlFormatter

        formatter = HtmlFormatter(cssclass=PYGMENTS_STYLE)
        css_defs = formatter.get_style_defs()

        with open(os.path.join(OUTPUT_DIR,'code_styles.css'),'w') as css_file:
            css_file.write(css_defs)
