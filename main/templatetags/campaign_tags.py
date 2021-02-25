from django import template

register = template.Library()


@register.filter('is_selected')
def is_selected(campaign, selected):
    return True if campaign.name == selected else False
