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

        self.posts = sorted(post_list, key=lambda p: p.updated)

        self._check_monotonic()
        self._resolve_links()
        
        for post in self.posts:
            errors = post.get_errors()
            for error in errors:
                print 'Error in',post.filename,'on line',str(error.line)+': ',error.message,
                if error.text: print '('+error.text+')'
                print

    @property
    def tag_dict(self):
        tag_dict = defaultdict(list)
        for post in self.posts:
            for tag in post.tags:
                tag_dict[tag].append(post)
        return tag_dict

    def _resolve_links(self):
        import re
        from itertools import chain

        posts = dict((p.id,p) for p in self.posts)

        def repl_link(match):
            pdw_id = int(match.group('pdw_id'))
            post = posts.get(pdw_id)
            if post:
                return '`' + match.group(0) + ' </posts/'+posts[pdw_id].slug+'.html>`_'
            else:
                return match.group(0)

        intlink = re.compile('(PDW[-|\s]*?(?P<pdw_id>\d+))')

        for text_part in chain.from_iterable(p.text_parts for p in self.posts):
            text_part.text = intlink.sub(repl_link, text_part.text)

    def _check_monotonic(self):
        monotonic = True
        cur_max_id = 0
        for post in self.posts:
            if cur_max_id > post.id:
                print 'Warning:',cur_max_id,'appears to be out of order (publish date is before',pid,').'
                monotonic = False
            else:
                cur_max_id = post.id
        return monotonic

    def render(self):
        self.render_home()
        self.render_feeds()
        self.render_posts()
        self.render_tag_pages()
        self.render_css()

        import pdb;pdb.set_trace()
        return


    @requires_pub_dir
    def render_home(self):
        from settings import POSTS_PER_PAGE as ppp
        
        posts = [ p for p in self.posts[::-1] if not p.is_draft ]

        groups = group_posts(posts, ppp)

        last_page = len(groups)
        for cur_page, group in enumerate(groups, start=1):
            filename = 'posts/page_'+str(cur_page)+'.html'

            with open(os.path.join(OUTPUT_DIR, filename), 'w') as p_file:
                p_file.write(render_to('post_list.html', 
                                       posts=group, 
                                       cur_page=cur_page, 
                                       last_page=last_page))



    @requires_pub_dir
    def render_posts(self):
        with open(os.path.join(OUTPUT_DIR,'post_list.html'),'w') as pl_file:
            pl_file.write(render_to('post_list.html', posts=self.posts))

        for post in self.posts:
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
    def render_feeds(self):
        posts = [p for p in self.posts if not p.is_draft]
        with open(os.path.join(OUTPUT_DIR, 'feed', 'atom.xml'), 'w') as a_file:
            a_file.write(render_to('atom.mako', posts=posts))

    @requires_pub_dir
    def render_css(self):
        from settings import PYGMENTS_STYLE
        from pygments.formatters import HtmlFormatter

        formatter = HtmlFormatter(cssclass=PYGMENTS_STYLE)
        css_defs = formatter.get_style_defs()

        with open(os.path.join(OUTPUT_DIR,'code_styles.css'),'w') as css_file:
            css_file.write(css_defs)

def group_posts(posts, size):
    groups = []
    g_start = g_end = 0
    while g_end < len(posts):
        g_end = min( g_start+size, len(posts) )
        groups.append(posts[g_start:g_end])
        g_start = g_end
    return groups
