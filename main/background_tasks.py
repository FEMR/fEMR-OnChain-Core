from datetime import timedelta
from background_task import background
from pytz import timezone

from main.models import Campaign, Patient, PatientEncounter


@background(queue='close-encounters')
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


run_encounter_close = lambda x: close_encounters(repeat=86400)