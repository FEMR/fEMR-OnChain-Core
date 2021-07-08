from django import template

register = template.Library()


@register.filter('temp_round')
def temp_round(temp):
    if temp is not None:
        return round(temp, 2)
    else:
        return None
