"""
Non-view functions used to carry out background processes.
"""
import os
from datetime import timedelta

from django.db.models.query_utils import Q
from django.utils import timezone
from django.core.mail import send_mail

from silk.profiling.profiler import silk_profile

from main.models import (
    Campaign,
    Patient,
    PatientEncounter,
    UserSession,
    cal_key,
    fEMRUser,
)


@silk_profile("run-encounter-close")
def run_encounter_close(campaign: Campaign):
    """
    When triggered, this function will search for expired PatientEncounter
    objects and set them as inactive.
    """
    now = timezone.now()

    close_time = campaign.encounter_close
    delta = now - timedelta(days=close_time)

    patients = Patient.objects.filter(campaign=campaign)
    encounters = PatientEncounter.objects.filter(
        Q(patient__in=patients) & Q(active=True) & Q(timestamp__lt=delta)
    )
    for encounter in encounters:
        encounter.active = False
        encounter.save_no_timestamp()


@silk_profile("run-user-deactivate")
def run_user_deactivate(now=timezone.now()):
    """
    Mark any users who haven't logged in in a month as inactive,
    then let them know in an email.
    """
    delta = now - timedelta(days=30)
    for user in fEMRUser.objects.filter(is_active=True):
        if user.last_login is not None and user.last_login < delta:
            if os.environ.get("EMAIL_HOST") != "":
                send_mail(
                    "Message from fEMR OnChain",
                    "We noticed you haven't logged in to fEMR OnChain in "
                    "quite a while. We're going to lock your account for now."
                    "\n\nYou'll be able to have it reactivated if you "
                    "need it again."
                    "\n\n\nTHIS IS AN AUTOMATED MESSAGE. "
                    "PLEASE DO NOT REPLY TO THIS EMAIL.",
                    os.environ.get("DEFAULT_FROM_EMAIL"),
                    [user.email],
                )
            user.is_active = False
            user.save()


@silk_profile("reset-sessions")
def reset_sessions() -> None:
    """
    Empty out sessions older than 1 minute.
    :return: None.
    """
    now = timezone.now()
    delta = now - timedelta(minutes=1)
    for session in UserSession.objects.all():
        if session.timestamp < delta:
            session.delete()


@silk_profile("check-browser")
def check_browser(request) -> bool:
    print(request.user_agent.browser.family)
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


@silk_profile("check-admin-permission")
def check_admin_permission(user):
    """
    Given a user, check whether that user is a member of an
    administrative group. The current admin groups are
    fEMR Admin, Campaign Manager, Organization Admin, and
    Operation Admin.

    :param user: A user to check for permissions.
    :return: Whether the user is in an administrative group.
    """
    return user.groups.filter(
        Q(name="fEMR Admin")
        | Q(name="Campaign Manager")
        | Q(name="Organization Admin")
        | Q(name="Operation Admin")
    ).exists()


@silk_profile("assign-broken-patients")
def assign_broken_patient():
    """
    Skim the database for patients with a campaign_key of
    None and make sure they get a correct key.

    :return: None
    """
    for patient in Patient.objects.filter(campaign_key=None):
        patient.campaign_key = cal_key(patient.id)
        patient.save()
