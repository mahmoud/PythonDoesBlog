def slugify(value):
    """straight up stolen out of django"""
    import unicodedata, re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s_]', '', value).strip().lower())
    return re.sub('[_\s]+', '_', value)
