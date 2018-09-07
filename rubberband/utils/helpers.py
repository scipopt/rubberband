
def shortening_span(text, short):
    """
    get a span with text that shortenes itself on small screens (use in table column headers)
    """
    return '''<span class="d-none d-xl-block">{longtext}</span>
    <span class="d-block d-xl-none" title="{longtext}">{shorttext}</span>
    '''.format(longtext=text, shorttext=short)

def get_link(href, text, length=30, end=10):
    """
    get a link with shortened text to href and full text as title
    """
    link = '<a href="{}" title="{}">{}</a>'.format(href, text, shorten_str(text, length, end))
    return link

def shorten_str(string, length=30, end=10):
    """
    Shorten a string to the given length.
    """
    if len(string) <= length:
        return string
    else:
        return "{}...{}".format(string[:length-end], string[-end:])
