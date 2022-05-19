"""
Non-view functions used to carry out background processes.
"""
import os
from datetime import timedelta, datetime
from celery import shared_task

from django.db.models.query_utils import Q
from django.utils import timezone
from django.core.mail import send_mail

from silk.profiling.profiler import silk_profile
from model_bakery import baker

from main.models import (
    CSVExport,
    Campaign,
    Patient,
    PatientEncounter,
    UserSession,
    cal_key,
    fEMRUser,
)


@shared_task
@silk_profile("run-encounter-close")
def run_encounter_close():
    """
    When triggered, this function will search for expired PatientEncounter
    objects and set them as inactive.
    """
    now = timezone.now()

    for campaign in Campaign.objects.all().iterator():
        close_time = campaign.encounter_close
        delta = now - timedelta(days=close_time)

        patients = Patient.objects.filter(campaign=campaign)
        encounters = PatientEncounter.objects.filter(
            Q(patient__in=patients) & Q(active=True) & Q(timestamp__lt=delta)
        )
        for encounter in encounters:
            encounter.active = False
            encounter.save_no_timestamp()


@shared_task
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


@shared_task
@silk_profile("reset-sessions")
def reset_sessions() -> None:
    """
    Empty out sessions older than 1 minute.
    :return: None.
    """
    now = timezone.now()
    delta = now - timedelta(minutes=1)
    for session in UserSession.objects.filter(timestamp__lt=delta):
        session.delete()


@silk_profile("check-browser")
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
    admin_groups = {
        "fEMR Admin",
        "Campaign Manager",
        "Organization Admin",
        "Operation Admin",
    }
    user_groups = {group.name for group in user.groups.all().iterator()}
    return admin_groups.intersection(user_groups)


@shared_task
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


@shared_task
@silk_profile("delete-old-export")
def delete_old_export():
    now = timezone.now()
    delta = now - timedelta(weeks=2)
    for export in CSVExport.objects.filter(timestamp__lt=delta).iterator():
        export.delete()


@shared_task
@silk_profile("assign_new_timestamp")
def assign_new_timestamp():
    now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
    now = now.astimezone(timezone.get_current_timezone())
    for patient in Patient.objects.filter(
        (Q(patientencounter__timestamp__date=now) | Q(timestamp__date=now))
    ).order_by("-timestamp"):
        if patient.patientencounter_set.count() > 0:
            patient.timestamp = (
                patient.patientencounter_set.all().order_by("-timestamp")[0].timestamp
            )
            patient.save()


@shared_task
@silk_profile("stress-test")
def start_stress_test(campaign_name):
    campaign = Campaign.objects.get_or_create(name=campaign_name)[0]
    for _ in range(1000):
        patient = baker.make("main.Patient")
        patient.campaign.add(campaign)
        for _ in range(10):
            encounter = baker.make("main.PatientEncounter")
            encounter.patient = patient
            encounter.campaign = campaign
            encounter.save()