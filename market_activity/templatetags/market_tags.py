from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def divide_by(obj, attr):
    try:
        decimal_attr = Decimal(attr)
        decimal_obj = Decimal(obj)
    except:
        return None
    if decimal_attr == 0:
        return None
    return decimal_obj/decimal_attr
