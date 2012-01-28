def slugify(value):
    """straight up stolen out of django"""
    import unicodedata, re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s_]', '', value).strip().lower())
    return re.sub('[_\s]+', '_', value)

# TODO: refactor to check/incrementally create directory structure
def requires_pub_dir(f): 
    from settings import OUTPUT_DIR
    from functools import wraps

    @wraps(f)
    def g(*args, **kwargs):
        import sys, os
        try:
            os.listdir(OUTPUT_DIR)
        except OSError as ose:
            try:
                os.mkdir(OUTPUT_DIR)
                os.mkdir(os.path.join(OUTPUT_DIR,'posts'))
                os.mkdir(os.path.join(OUTPUT_DIR,'feed'))
                os.mkdir(os.path.join(OUTPUT_DIR,'tags'))
            except OSError as ose2:
                print 'Publishing directory structure could not be created under',OUTPUT_DIR
                sys.exit(1)
        return f(*args, **kwargs)
    return g

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

