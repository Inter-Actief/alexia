from django import template
from django.urls import Resolver404, resolve

register = template.Library()


@register.simple_tag(takes_context=True)
def active_menu(context, pattern, css_class=' active'):
    if 'request' not in context:
        return ''

    try:
        func = resolve(context['request'].path).func
        string = "%s.%s" % (func.__module__, func.__name__)
        import re
        if re.search(pattern, string):
            return css_class
    except Resolver404:
        pass

    return ''
