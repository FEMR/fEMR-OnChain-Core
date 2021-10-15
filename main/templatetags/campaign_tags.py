"""
TemplateTags used to carry out more complex display actions on Campaigns.
"""
from django import template

from main.models import Campaign

register = template.Library()


@register.filter('is_selected')
def is_selected(campaign: Campaign, selected: str) -> bool:
    """
    Given a campaign and a campaign name, check if they match.
    :param campaign:
    :param selected:
    :return:
    """
    return True if campaign.name == selected else False
