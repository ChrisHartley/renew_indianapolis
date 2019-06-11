from django import template
from django.template.defaultfilters import stringfilter
from datetime import timedelta, datetime, date
from num2words import num2words as num2words_orig

register = template.Library()

@register.filter
def num2words(value):
    """Returns a string/word representation of a number"""
    try:
        val = float(value)
        return num2words_orig(value)
    except ValueError:

#    if type(value) in [long, int, float]:
#        return num2words_orig(value)
#    else:
        return "ERROR - {}".format(value,)
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

@register.filter
def multiply(value, arg):
    try:
        answer = float(value) * float(arg)
    except:
        answer = "Error"
    finally:
        return answer
