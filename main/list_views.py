"""
View functions handling displaying data models as sortable, filterable lists.

All views, except auth views and the index view, should be considered
to check for a valid and authenticated user.

If one is not found, they will direct to the appropriate error page.
"""
import itertools
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from silk.profiling.profiler import silk_profile

from main.csvio.patient_csv_export import run_patient_csv_export

from .models import (
    ChiefComplaint,
    PatientEncounter,
    Patient,
    Campaign,
)


def get_latest_timestamp(patient):
    try:
        return (
            PatientEncounter.objects.filter(patient=patient)
            .order_by("-timestamp")[0]
            .timestamp
        )
    except IndexError:
        return patient.timestamp


def patient_list_view(request):
    """
    Administrative/Clinician list of patients entered into the system.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        try:
            patients = Patient.objects.filter(
                campaign=Campaign.objects.get(name=request.session["campaign"])
            )
            now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
            now = now.astimezone(timezone.get_current_timezone())
            data = set(
                list(
                    itertools.chain(
                        patients.filter(patientencounter__timestamp__date=now),
                        patients.filter(timestamp__date=now),
                    )
                )
            )
        except ObjectDoesNotExist:
            data = []
        data = sorted(data, reverse=True, key=get_latest_timestamp)
        paginator = Paginator(data, 25)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return_response = render(
            request,
            "list/patient.html",
            {
                "user": request.user,
                "page_obj": page_obj,
                "page_name": "Manager",
                # pylint: disable=C0301
                "page_tip": "This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.",
            },
        )
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def patient_csv_export_view(request):
    """
    CSV Export of an Administrative/Clinician list of patients entered into the system.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        return_response = run_patient_csv_export(request)
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


@silk_profile("--run-patient-list-filter-one")
def __run_patient_list_filter_one(request, campaign):
    now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
    now = now.astimezone(timezone.get_current_timezone())
    data = (
        Patient.objects.filter(campaign=campaign)
        .filter(Q(patientencounter__timestamp__date=now) | Q(timestamp__date=now))
        .distinct()
    )
    return data


@silk_profile("--run-patient-list-filter-two")
def __run_patient_list_filter_two(request, campaign):
    timestamp_from = timezone.now() - timedelta(days=7)
    timestamp_to = timezone.now()
    data = (
        Patient.objects.filter(campaign=campaign)
        .filter(
            Q(
                patientencounter__timestamp__gte=timestamp_from,
                patientencounter__timestamp__lt=timestamp_to,
            )
            | Q(
                timestamp__gte=timestamp_from,
                timestamp__lt=timestamp_to,
            )
        )
        .distinct()
    )
    return data


@silk_profile("--run-patient-list-filter-three")
def __run_patient_list_filter_three(request, campaign):
    timestamp_from = timezone.now() - timedelta(days=30)
    timestamp_to = timezone.now()
    data = (
        Patient.objects.filter(campaign=campaign)
        .filter(
            Q(
                patientencounter__timestamp__gte=timestamp_from,
                patientencounter__timestamp__lt=timestamp_to,
            )
            | Q(
                timestamp__gte=timestamp_from,
                timestamp__lt=timestamp_to,
            )
        )
        .distinct()
    )
    return data


@silk_profile("--run-patient-list-filter-four")
def __run_patient_list_filter_four(request, campaign):
    try:
        timestamp_from = datetime.strptime(
            request.GET["date_filter_day"], "%Y-%m-%d"
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp_to = datetime.strptime(
            request.GET["date_filter_day"], "%Y-%m-%d"
        ).replace(hour=23, minute=59, second=59, microsecond=0)
        data = (
            Patient.objects.filter(campaign=campaign)
            .filter(
                Q(
                    patientencounter__timestamp__gte=timestamp_from,
                    patientencounter__timestamp__lt=timestamp_to,
                )
                | Q(
                    timestamp__gte=timestamp_from,
                    timestamp__lt=timestamp_to,
                )
            )
            .distinct()
        )
    except ValueError:
        data = []
    return data


@silk_profile("--run-patient-list-filter-five")
def __run_patient_list_filter_five(request, campaign):
    try:
        timestamp_from = datetime.strptime(request.GET["date_filter_start"], "%Y-%m-%d")
        timestamp_to = datetime.strptime(
            request.GET["date_filter_end"], "%Y-%m-%d"
        ) + timedelta(days=1)
        data = (
            Patient.objects.filter(campaign=campaign)
            .filter(
                Q(
                    patientencounter__timestamp__gte=timestamp_from,
                    patientencounter__timestamp__lt=timestamp_to,
                )
                | Q(
                    timestamp__gte=timestamp_from,
                    timestamp__lt=timestamp_to,
                ),
            )
            .distinct()
        )
    except ValueError:
        data = []
    return data


@silk_profile("--run-patient-list-filter")
def __run_patient_list_filter(request):
    current_campaign = Campaign.objects.get(name=request.session["campaign"])
    try:
        if request.GET["filter_list"] == "1":
            data = __run_patient_list_filter_one(request, current_campaign)
        elif request.GET["filter_list"] == "2":
            data = __run_patient_list_filter_two(request, current_campaign)
        elif request.GET["filter_list"] == "3":
            data = __run_patient_list_filter_three(request, current_campaign)
        elif request.GET["filter_list"] == "4":
            data = __run_patient_list_filter_four(request, current_campaign)
        elif request.GET["filter_list"] == "5":
            data = __run_patient_list_filter_five(request, current_campaign)
        elif request.GET["filter_list"] == "6":
            try:
                data = Patient.objects.filter(campaign=current_campaign)
            except ValueError:
                data = []
        else:
            data = []
    except ObjectDoesNotExist:
        data = []
    return data


@silk_profile("filter-patient-list-view")
def filter_patient_list_view(request):
    """
    Runs a search of all patients, using a name entered on the List page.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = __run_patient_list_filter(request)
        data = sorted(data, reverse=True, key=get_latest_timestamp)
        paginator = Paginator(data, 25)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return_response = render(
            request,
            "list/patient.html",
            {
                "user": request.user,
                "page_name": "Manager",
                "page_obj": page_obj,
                "selected": int(request.GET["filter_list"]),
                "filter_day": request.GET["date_filter_day"],
                "filter_start": request.GET["date_filter_start"],
                "filter_end": request.GET["date_filter_end"],
                # pylint: disable=C0301
                "page_tip": "This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.",
            },
        )
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def search_patient_list_view(request):
    """
    Runs a search of all patients, using a name entered on the List page.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        try:
            current_campaign = Campaign.objects.get(name=request.session["campaign"])
            patients = Patient.objects.filter(campaign=current_campaign)
            for term in request.GET["name_search"].split():
                data = set(
                    list(
                        itertools.chain(
                            patients.filter(
                                Q(campaign_key__icontains=request.GET["name_search"])
                                | Q(first_name__icontains=request.GET["name_search"])
                                | Q(last_name__icontains=request.GET["name_search"])
                                | Q(phone_number__icontains=request.GET["name_search"])
                                | Q(
                                    phone_number__icontains=__parse_phone_number(
                                        request.GET["name_search"]
                                    )
                                )
                                | Q(email_address__iexact=request.GET["name_search"])
                            ),
                            patients.filter(
                                Q(first_name__icontains=term)
                                | Q(last_name__icontains=term)
                            ),
                        )
                    )
                )
        except ObjectDoesNotExist:
            data = []
        data = sorted(data, reverse=True, key=get_latest_timestamp)
        paginator = Paginator(data, 25)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return_response = render(
            request,
            "list/patient.html",
            {
                "user": request.user,
                "page_obj": page_obj,
                # pylint: disable=C0301
                "page_tip": "This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.",
            },
        )
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def __parse_phone_number(input_string):
    if len(input_string) < 10 or len(input_string) > 10:
        return_response = input_string
    else:
        return_response = (
            f"({input_string[0:3]}){input_string[3:6]}-{input_string[6:10]}"
        )
    return return_response


def chief_complaint_list_view(request, patient_id=None, encounter_id=None):
    if request.user.is_authenticated:
        return_response = render(
            request,
            "list/chief_complaint.html",
            {
                "list_view": ChiefComplaint.objects.filter(active=True),
                "patient_id": patient_id,
                "encounter_id": encounter_id,
                "new": (encounter_id is None),
            },
        )
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
