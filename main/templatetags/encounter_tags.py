from django import template

register = template.Library()


@register.filter("temp_round")
def temp_round(temp):
    return round(temp, 2) if temp is not None else None
