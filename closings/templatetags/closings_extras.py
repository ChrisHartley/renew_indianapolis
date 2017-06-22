from django import template
from django.template.defaultfilters import stringfilter
from datetime import timedelta, datetime, date
from num2words import num2words as num2words_orig

register = template.Library()

@register.filter
def num2words(value):
    """Returns a string/word representation of a number"""
    return num2words_orig(value)

@register.filter
def plus_30_days(value):
    """Returns now plus 30 days, an ugly hack"""
    return date.today() + timedelta(days=30)

@register.filter
def plus_n_days(value, arg):
    """Returns now plus n days, an ugly hack"""
    if arg is None:
        return False
    return date.today() + timedelta(days=int(arg))
