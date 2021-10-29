"""
Non-view functions used to carry out background processes.
"""
from datetime import timedelta
from django.db.models.query_utils import Q

from django.utils import timezone
from silk.profiling.profiler import silk_profile

from main.models import Campaign, Patient, PatientEncounter, UserSession


@silk_profile("run-encounter-close")
def run_encounter_close(campaign: Campaign):
    """
    When triggered, this function will search for expired PatientEncounter
    objects and set them as inactive.
    """
    now = timezone.now()

    close_time = campaign.encounter_close
    d = now - timedelta(days=close_time)
    patients = Patient.objects.filter(campaign=campaign)
    for p in patients:
        encounters = PatientEncounter.objects.filter(patient=p)
        for e in encounters:
            if e.timestamp < d:
                e.active = False
                e.save_no_timestamp()


@silk_profile("reset_sessions")
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


@silk_profile("check_browser")
def check_browser(request) -> bool:
    if request.user_agent.browser.family not in [
        "Chrome",
        "Firefox",
        "Firefox Mobile",
        "Chrome Mobile iOS",
        "Other",
    ]:
        retval = False
    else:
        retval = True
    return retval


def check_admin_permission(user):
    return user.groups.filter(
        Q(name="fEMR Admin")
        | Q(name="Campaign Manager")
        | Q(name="Organization Admin")
        | Q(name="Operation Admin")
    ).exists()
