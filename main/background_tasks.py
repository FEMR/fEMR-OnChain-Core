"""
Non-view functions used to carry out background processes.
"""
import os
from datetime import timedelta
from django.contrib.auth.models import Group
from django.db.models.query_utils import Q

from django.utils import timezone
from silk.profiling.profiler import silk_profile
from django.core.mail import send_mail

from main.models import Campaign, Patient, PatientEncounter, UserSession, fEMRUser


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


@silk_profile("run-user-deactivate")
def run_user_deactivate(now=timezone.now()):
    """
    Mark any users who haven't logged in in a month as inactive,
    then let them know in an email.
    """
    d = now - timedelta(days=30)
    for user in fEMRUser.objects.filter(is_active=True):
        if user.last_login is not None and user.last_login < d:
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
    :return:
    """
    now = timezone.now()
    d = now - timedelta(minutes=1)
    for x in UserSession.objects.all():
        if x.timestamp < d:
            x.delete()


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
    return user.groups.filter(
        Q(name="fEMR Admin")
        | Q(name="Campaign Manager")
        | Q(name="Organization Admin")
        | Q(name="Operation Admin")
    ).exists()


@silk_profile("reassign-admin-groups")
def reassign_admin_groups(user):
    if user.groups.filter(name="Admin").exists():
        user.groups.add(Group.objects.get(name="Campaign Manager"))
        user.groups.remove(Group.objects.get(name="Admin"))
    if Group.objects.filter(name="Admin").exists():
        admin_group = Group.objects.get(name="Admin")
        if len(admin_group.user_set.all()) == 0:
            admin_group.delete()
