# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import math

# Core Django imports
from django import template

# Stdlib imports

# Third-party app imports

# Relative imports of the 'app-name' package


register = template.Library()


@register.filter("has_suffix")
def has_suffix(patient):
    return patient.get_suffix_display() if patient.suffix is not None else ""


@register.filter("open_encounters")
def open_encounters(patient):
    return (
        "Yes"
        if len(patient.patientencounter_set.filter(patient=patient).filter(active=True))
        > 0
        else ""
    )


@register.filter("has_middle_name")
def has_middle_name(patient):
    return patient.middle_name if patient.middle_name is not None else ""


@register.filter("last_timestamp")
def last_timestamp(patient):
    try:
        return patient.patientencounter_set.order_by("-timestamp")[0].timestamp
    except IndexError:
        return patient.timestamp


@register.filter("mask_social")
def mask_social(social):
    if social is None:
        retval = ""
    elif len(social) == 4:
        retval = f"***-**-{social}"
    else:
        retval = f"***-**-{social[7:11]}"
    return retval


@register.filter("get_chief_complaint")
def get_chief_complaint(encounter):
    return ",".join([str(e) for e in encounter.chief_complaint.all()])


@register.filter("imperial_primary_height")
def imperial_primary_height(item):
    return math.floor(
        ((item.body_height_primary * 100 + item.body_height_secondary) / 2.54) // 12
    )


@register.filter("imperial_secondary_height")
def imperial_secondary_height(item):
    return round(
        ((item.body_height_primary * 100 + item.body_height_secondary) / 2.54) % 12, 2
    )


@register.filter("imperial_weight")
def imperial_weight(item):
    return round(item.body_weight * 2.2046, 2)


@register.filter("imperial_temperature")
def imperial_temperature(item):
    return (
        round((item.body_temperature * 9 / 5) + 32, 2)
        if item.body_temperature is not None
        else None
    )


@register.filter("complaint_as_string")
def complaint_as_string(item):
    result = ""
    for element in list(item.all()):
        result += str(element) + ", "
    return result


@register.filter("get_campaign_info")
def get_campaign_info(item):
    result = ""
    for element in list(item.campaign.all()):
        result += str(element) + ", "
    return result


@register.filter("get_medications")
def get_medications(treatment):
    result = ""
    for element in list(treatment.medication.all()):
        result += str(element)
    return result


@register.filter("get_amount")
def get_amount(item):
    return item.count * item.quantity
