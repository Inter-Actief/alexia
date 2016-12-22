# Defines filters we can use to perform calculations in the views.

from django import template

register = template.Library()


@register.filter
def add(value, arg):
    return int(value) + int(arg)


@register.filter
def substract(value, arg):
    return int(value) - int(arg)


@register.filter
def multiply(value, arg):
    return int(float(value) * float(arg))


@register.filter
def divide(value, arg):
    return int(float(value) / float(arg))


@register.filter
def modulo(value, arg):
    return int(value) % int(arg)
