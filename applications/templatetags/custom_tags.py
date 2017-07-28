from django import template
register = template.Library()

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

@register.filter()
def divide(n1, n2):
    try:
        return n1 / n2
    except ZeroDivisionError:
        return None

@register.filter()
def multiply(n1, n2):
    return n1 * n2

@register.filter()
def percentof(amount, total):
    try:
        return '{:.1f}%'.format(float(amount) / float(total) * 100)
    except ZeroDivisionError:
        return None
