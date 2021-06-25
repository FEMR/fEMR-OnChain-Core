from datetime import timedelta
from pytz import timezone

from main.models import Campaign, Patient, PatientEncounter


def close_encounters():
    campaigns = Campaign.objects.all()
    now = timezone.now()

    for c in campaigns:
        close_time = c.encounter_close
        d = now - timedelta(days=close_time)
        patients = Patient.objects.filter(campaign=c)
        for p in patients:
            encounters = PatientEncounter.objects.filter(patient=p)
            for e in encounters:
                if e.timestamp >= d:
                    e.active = False
