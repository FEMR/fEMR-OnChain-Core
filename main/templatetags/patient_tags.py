# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import math

# Core Django imports
from django import template

from main.models import PatientEncounter

# Stdlib imports

# Third-party app imports

# Relative imports of the 'app-name' package


register = template.Library()


@register.filter('has_suffix')
def has_suffix(patient):
    return patient.get_suffix_display() if patient.suffix is not None else ""


@register.filter('open_encounters')
def open_encounters(patient):
    return "Yes" if len(PatientEncounter.objects.filter(patient=patient).filter(active=True)) > 0 else ""


@register.filter('has_middle_name')
def has_middle_name(patient):
    return patient.middle_name if patient.middle_name is not None else ""


@register.filter('last_timestamp')
def last_timestamp(patient):
    try:
        return PatientEncounter.objects.filter(patient=patient).order_by('-timestamp')[0].timestamp
    except IndexError:
        return patient.timestamp


@register.filter('mask_social')
def mask_social(patient):
    if patient is None:
        return ""
    if len(patient) == 4:
        return "***-**-{}".format(patient)
    else:
        return "***-**-{}".format(patient[7:11])


@register.filter('get_chief_complaint')
def get_chief_complaint(encounter):
    return ",".join([str(e) for e in encounter.chief_complaint.all()])


@register.filter('imperial_primary_height')
def imperial_primary_height(m):
    print(m.body_height_primary)
    print(m.body_height_secondary)
    return math.floor(((m.body_height_primary * 100 + m.body_height_secondary) / 2.54) // 12)


@register.filter('imperial_secondary_height')
def imperial_secondary_height(m):
    return round(((m.body_height_primary * 100 + m.body_height_secondary) / 2.54) % 12, 2)


@register.filter('imperial_weight')
def imperial_weight(m):
    return round(m.body_weight * 2.2046, 2)


@register.filter('imperial_temperature')
def imperial_temperature(m):
    if m.body_temperature is not None:
        return round((m.body_temperature * 9 / 5) + 32, 2)
    else:
        return None


@register.filter('complaint_as_string')
def complaint_as_string(m):
    result = ""
    for x in list(m.all()):
        result += str(x) + ", "
    return result


@register.filter('get_campaign_info')
def get_campaign_info(m):
    result = ""
    for x in list(m.campaign.all()):
        result += str(x) + ", "
    return result


@register.filter('get_medications')
def get_medications(t):
    result = ""
    for x in list(t.medication.all()):
        result += str(x)
    return result
