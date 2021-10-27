"""
Django TemplateTags for processing complex logic interacting with fEMRUser objects in templates.
"""
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

# Core Django imports
from django import template
from django.db.models.query_utils import Q

from main.models import Campaign, fEMRUser

# Stdlib imports

# Third-party app imports

# Relative imports of the 'app-name' package


register = template.Library()


@register.filter("has_group")
def has_group(user: fEMRUser, group_name: str) -> bool:
    """
    Given group_name, return whether user is a member of that group.
    :param user:
    :param group_name:
    :return:
    """
    groups = user.groups.all().values_list("name", flat=True)
    return True if group_name in groups else False


@register.filter("has_campaign")
def has_campaign(user: fEMRUser, campaign_name: str) -> bool:
    """
    Given a campaign name, return whether user is a member of that campaign.
    :param user:
    :param campaign_name:
    :return:
    """
    campaign = Campaign.objects.get(name=campaign_name)
    campaign_list = user.campaigns.all()
    return True if campaign in campaign_list else False


@register.filter("campaign_active")
def campaign_active(campaign_name: str) -> bool:
    """
    Return whether the given campaign_name refers to an active campaign.
    :param campaign_name:
    :return:
    """
    return Campaign.objects.get(name=campaign_name).active


@register.filter("has_any_group")
def has_any_group(user: fEMRUser) -> bool:
    return user.groups.all()


@register.filter("has_admin_group")
def has_admin_group(user: fEMRUser) -> bool:
    return user.groups.filter(
        Q(name="Campaign Manager")
        | Q(name="Organization Admin")
        | Q(name="Operation Admin")
    ).exists()
