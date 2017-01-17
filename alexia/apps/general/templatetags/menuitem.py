import re

from django.template import Library, Node, TemplateSyntaxError
from django.template.base import token_kwargs
from django.urls import resolve
from django.utils.html import format_html

register = Library()


class MenuItemNode(Node):
    def __init__(self, nodelist, pattern, kwargs):
        self.nodelist = nodelist
        self.pattern = pattern
        self.kwargs = kwargs

    def render(self, context):
        pattern = self.pattern.resolve(context)

        classes = []
        if 'class' in self.kwargs:
            classes = self.kwargs['class'].resolve(context).split()

        func = resolve(context['request'].path).func
        match = func.__module__ + '.' + func.__name__
        if re.search(pattern, match):
            classes.append('active')

        if classes:
            open_tag = format_html('<li class="{}">', ' '.join(classes))
        else:
            open_tag = format_html('<li>')

        content = self.nodelist.render(context)
        close_tag = format_html('</li>')
        return open_tag + content + close_tag


@register.tag
def menuitem(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument, a pattern matching a view name." % bits[0])
    pattern = parser.compile_filter(bits[1])
    kwargs = token_kwargs(bits[2:], parser)

    nodelist = parser.parse(('endmenuitem',))
    parser.delete_first_token()
    return MenuItemNode(nodelist, pattern, kwargs)
