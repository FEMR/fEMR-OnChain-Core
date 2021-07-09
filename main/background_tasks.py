from datetime import timedelta
from django.utils import timezone

from main.models import Campaign, Patient, PatientEncounter


def run_encounter_close():
    print("Checking for encounter closure.")
    campaigns = Campaign.objects.all()
    now = timezone.now()

    for c in campaigns:
        close_time = c.encounter_close
        d = now - timedelta(days=close_time)
        patients = Patient.objects.filter(campaign=c)
        for p in patients:
            encounters = PatientEncounter.objects.filter(patient=p)
            for e in encounters:
                if e.timestamp < d:
                    print("Set {0} inactive.".format(e))
                    e.active = False
                    e.save_no_timestamp()
