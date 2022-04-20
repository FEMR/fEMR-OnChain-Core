from django import template

from django.utils import timezone
from datetime import datetime
from main.models import Patient, PatientEncounter

register = template.Library()


@register.filter("patients_today")
def patients_today(campaign):
    now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
    now = now.astimezone(timezone.get_current_timezone())
    return Patient.objects.filter(campaign=campaign).filter(timestamp__date=now).count()


@register.filter("total_patients")
def total_patients(campaign):
    return Patient.objects.filter(campaign=campaign).count()


@register.filter("encounters_today")
def encounters_today(campaign):
    now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
    now = now.astimezone(timezone.get_current_timezone())
    return PatientEncounter.objects.filter(campaign=campaign).filter(timestamp__date=now).count()


@register.filter("total_encounters")
def total_encounters(campaign):
    return PatientEncounter.objects.filter(campaign=campaign).count()
