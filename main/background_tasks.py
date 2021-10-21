"""
Non-view functions used to carry out background processes.
"""
from datetime import timedelta

from django.utils import timezone

from main.models import Campaign, Patient, PatientEncounter, UserSession


def run_encounter_close():
    """
    When triggered, this function will search for expired PatientEncounter objects and set them as inactive.
    """
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


def reset_sessions() -> None:
    """
    Empty out sessions older than 1 minute.
    :return:
    """
    now = timezone.now()
    d = now - timedelta(minutes=1)
    for x in UserSession.objects.all():
        if x.timestamp < d:
            x.delete()


def check_browser(request) -> bool:
    print(request.user_agent.browser.family)
    if request.user_agent.browser.family not in ["Chrome", "Firefox", "Firefox Mobile", "Chrome Mobile iOS"]:
        print("Blocking browser.")
        return False
    else:
        print("Allowing browser.")
        return True