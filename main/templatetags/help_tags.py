from django import template

register = template.Library()


@register.filter('is_help_off')
def has_suffix(session):
    return True if session.get('tags_off', None) is not None else False
