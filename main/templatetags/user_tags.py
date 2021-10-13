# -*- coding:utf-8 -*-
from __future__ import unicode_literals

# Core Django imports
from django import template

from main.models import Campaign

# Stdlib imports

# Third-party app imports

# Relative imports of the 'app-name' package


register = template.Library()


@register.filter('has_group')
def has_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False


@register.filter('has_campaign')
def has_campaign(user, campaign_name):
    campaign = Campaign.objects.get(name=campaign_name)
    campaign_list = user.campaigns.all()
    return True if campaign in campaign_list else False


@register.filter('campaign_active')
def campaign_active(campaign_name):
    return Campaign.objects.get(name=campaign_name).active
