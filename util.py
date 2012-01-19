def slugify(value):
    """straight up stolen out of django"""
    import unicodedata, re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s_]', '', value).strip().lower())
    return re.sub('[_\s]+', '_', value)

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

