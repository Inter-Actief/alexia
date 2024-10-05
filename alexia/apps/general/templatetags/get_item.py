from django import template

register = template.Library()

@register.filter
def get_item(key, dictionary):
    return dictionary.get(key)
