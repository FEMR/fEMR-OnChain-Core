"""
TemplateTags used to carry out more complex display actions on Campaigns.
"""
from django import template

from main.models import Campaign

register = template.Library()


@register.filter("is_selected")
def is_selected(campaign: Campaign, selected: str) -> bool:
    return campaign.name == selected
