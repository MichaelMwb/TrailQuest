from django import template

register = template.Library()

@register.filter(name='split')
def split(value, delimiter):
  """
    Returns the value turned into a list.
  """
  return value.split(delimiter)