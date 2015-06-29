from django import template
from django.core.urlresolvers import resolve
from django.http import Http404

register = template.Library()


@register.simple_tag(takes_context=True)
def active_menu(context, expression, css_class='active'):
    import re

    # Skip if no context
    if 'request' not in context:
        return ''

    try:
        func, args, kwargs = resolve(context['request'].path)
    except Http404:
        # Invalid URL
        return ''

    haystack = "%s.%s" % (func.__module__, func.__name__)

    # Parse regular expression
    if re.search(expression, haystack):
        return css_class

    # Nothing
    return ''
