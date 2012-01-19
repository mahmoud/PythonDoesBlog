import os, imp, doctest, datetime
from collections import OrderedDict, defaultdict, namedtuple
from util import slugify, render_to

import settings
from settings import SOURCE_DIR, SOURCE_EXCLUDE, OUTPUT_DIR

from post import Post

def get_posts():
    post_list = []
    for file_path in os.listdir(SOURCE_DIR):
        if not file_path.endswith('.py') or file_path in SOURCE_EXCLUDE:
            continue

        full_path = os.path.join(SOURCE_DIR, file_path)
        try:
            post = Post(full_path)
            for error in post.rst_errors:
                print 'Error in',post.filename,'on line',str(error.line)+': ',error.message,
                if error.text: print '('+error.text+')'
            post_list.append(post)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print 'Error creating Post from '+str(full_path)+':'+str(e)
            continue
    
    posts = OrderedDict((p.id, p) for p in sorted(post_list, key=lambda p: p.date))
    
    return posts

def get_tag_dict(posts):
    tag_dict = defaultdict(list)
    for id, post in posts.items():
        for tag in post.tags:
            tag_dict[tag].append(post)
    return tag_dict

def check_monotonic(posts):
    monotonic = True
    cur_max_id = 0
    for (pid, post) in posts.items():
        if cur_max_id > pid:
            print 'Warning:',cur_max_id,'appears to be out of order (publish date is before',pid,').'
            monotonic = False
        else:
            cur_max_id = pid
    return monotonic

# TODO: refactor to check/incrementally create directory structure
def requires_pub_dir(f): 
    from functools import wraps
    @wraps(f)
    def g(*args, **kwargs):
        import sys
        try:
            os.listdir(OUTPUT_DIR)
        except OSError as ose:
            try:
                os.mkdir(OUTPUT_DIR)
                os.mkdir(os.path.join(OUTPUT_DIR,'posts'))
                os.mkdir(os.path.join(OUTPUT_DIR,'tags'))
            except OSError as ose2:
                print 'Publishing directory structure could not be created under',OUTPUT_DIR
                sys.exit(1)
        return f(*args, **kwargs)
    return g

@requires_pub_dir
def render_posts(posts):
    with open(os.path.join(OUTPUT_DIR,'post_list.html'),'w') as pl_file:
        pl_file.write(render_to('post_list.html', posts=posts.values()))

    for pid, post in posts.items():
        with open(os.path.join(OUTPUT_DIR, 'posts', post.slug+'.html'), 'w') as p_file:
            p_file.write(render_to('post_single.html', post=post))
                      
    return True

@requires_pub_dir
def render_tag_pages(tag_dict):
    for tag, posts in tag_dict.items():
        tag_slug = slugify(unicode(tag))
        with open(os.path.join(OUTPUT_DIR, 'tags', tag_slug+'.html'), 'w') as t_file:
            t_file.write(render_to('post_list.html', posts=posts))

@requires_pub_dir
def render_css():
    from settings import PYGMENTS_STYLE
    from pygments.formatters import HtmlFormatter

    formatter = HtmlFormatter(cssclass=PYGMENTS_STYLE)
    css_defs = formatter.get_style_defs()
    with open(os.path.join(OUTPUT_DIR,'code_styles.css'),'w') as css_file:
        css_file.write(css_defs)
    return

def generate():
    posts = get_posts()
    tag_dict  = get_tag_dict(posts)

    check_monotonic(posts)
    render_posts(posts)
    render_tag_pages(tag_dict)
    render_css()
    import pdb;pdb.set_trace()

# TODO: automatic linking to other PDWs via syntax PDWxxx where xxx is an integer ID

if __name__ == '__main__':
    generate()
