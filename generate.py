import os, imp, doctest, datetime
from collections import OrderedDict, namedtuple
import settings

source_dir = settings.SOURCE_DIR
posts      = OrderedDict()

from post import Post

def get_posts():
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
    
    posts = OrderedDict((p.id, p) for p in sorted(post_list, key=lambda p: p.date))
    
    return posts

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

def render_to(template_name, data=None, **kwargs):
    from settings import TEMPLATE_DIRS
    from mako.lookup import TemplateLookup

    data = data or {}
    data.update(kwargs)
    try:
        lookup   = TemplateLookup(directories=TEMPLATE_DIRS)
        template = lookup.get_template(template_name)
        rendered = template.render_unicode(**data)
    except Exception as e:
        from mako import exceptions
        print exceptions.text_error_template().render()
    return rendered

def render_posts(posts):
    from settings import OUTPUT_DIR
    try:
        os.listdir(OUTPUT_DIR)
    except OSError as ose:
        try:
            os.mkdir(OUTPUT_DIR)
            os.mkdir(os.path.join(OUTPUT_DIR,'posts'))
        except OSError as ose2:
            print 'Output directory',OUTPUT_DIR,'does not exist and could not be created.'
            return False

    with open(os.path.join(OUTPUT_DIR,'post_list.html'),'w') as pl_file:
        pl_file.write(render_to('post_list.html', posts=posts))

    for pid, post in posts.items():
        with open(os.path.join(OUTPUT_DIR, 'posts', post.slug+'.html'), 'w') as p_file:
            p_file.write(render_to('post_single.html', post=post))
                      
    return True

def generate():
    posts = get_posts()
    check_monotonic(posts)
    post_list = render_posts(posts)
    import pdb;pdb.set_trace()

# TODO: automatic linking to other PDWs via syntax PDWxxx where xxx is an integer ID

if __name__ == '__main__':
    generate()
