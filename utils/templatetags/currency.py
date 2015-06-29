from django.template import Library

register = Library()


@register.filter
def euro(euros, sign=True):
    if euros != 0 and not euros:
        return ''
    # try:
    #    locale.setlocale(locale.LC_ALL, 'nl_NL')
    #    value = locale.currency(euros, symbol=False, grouping=True)
    # except:
    if True:
        import re

        value = "%.2f" % euros

        # For the thousands seperator
        reg = re.compile(r"(\d)(\d\d\d[., ])")
        while True:
            value, count = re.subn(reg, r"\1 \2", value)
            if not count:
                break
        value = value.replace(".", ",")

    if sign:
        return u"\u20AC\u00A0%s" % value
    else:
        return value
