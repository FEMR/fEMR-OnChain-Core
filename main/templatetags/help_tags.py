from django import template

register = template.Library()


@register.filter("is_help_off")
def is_help_off(session):
    return True if session.get("tags_off", None) is not None else False
