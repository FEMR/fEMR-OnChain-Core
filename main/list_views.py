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
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils import timezone
from silk.profiling.profiler import silk_profile

from main.csvio.patient_csv_export import run_patient_csv_export
from main.decorators import is_authenticated

from .models import (
    ChiefComplaint,
    Patient,
    Campaign,
)


@silk_profile("get-latest-timestamp")
def get_latest_timestamp(patient):
    try:
        return patient.patientencounter_set.all().order_by("-timestamp")[0].timestamp
    except IndexError:
        return patient.timestamp


@is_authenticated
@silk_profile("patient_list_view")
def patient_list_view(request):
    """
    Administrative/Clinician list of patients entered into the system.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    try:
        now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
        now = now.astimezone(timezone.get_current_timezone())
        data = list(
            Patient.objects.filter(
                (Q(patientencounter__timestamp__date=now) | Q(timestamp__date=now))
                & Q(campaign=Campaign.objects.get(name=request.user.current_campaign))
            )
        )
    except ObjectDoesNotExist:
        data = []
    data = sorted(data, reverse=True, key=get_latest_timestamp)
    paginator = Paginator(data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
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


@is_authenticated
def patient_csv_export_view(request, timeframe=1):
    """
    CSV Export of an Administrative/Clinician list of patients entered into the system.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    return run_patient_csv_export(request, timeframe)


@silk_profile("--run-patient-list-filter-one")
def __run_patient_list_filter_one(request, campaign):
    now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
    now = now.astimezone(timezone.get_current_timezone())
    data = Patient.objects.filter(
        Q(campaign=campaign)
        & (Q(patientencounter__timestamp__date=now) | Q(timestamp__date=now))
    ).distinct()
    return data


@silk_profile("--run_timestamp_filter")
def __run_timestamp_filter(campaign, timestamp_to, timestamp_from):
    return Patient.objects.filter(
        Q(campaign=campaign)
        & (
            Q(
                patientencounter__timestamp__gte=timestamp_from,
                patientencounter__timestamp__lt=timestamp_to,
            )
            | Q(
                timestamp__gte=timestamp_from,
                timestamp__lt=timestamp_to,
            )
        )
    ).distinct()


@silk_profile("--run-patient-list-filter-two")
def __run_patient_list_filter_two(_, campaign):
    timestamp_from = timezone.now() - timedelta(days=7)
    timestamp_to = timezone.now()
    return __run_timestamp_filter(campaign, timestamp_to, timestamp_from)


@silk_profile("--run-patient-list-filter-three")
def __run_patient_list_filter_three(_, campaign):
    timestamp_from = timezone.now() - timedelta(days=30)
    timestamp_to = timezone.now()
    return __run_timestamp_filter(campaign, timestamp_to, timestamp_from)


@silk_profile("--run-patient-list-filter-four")
def __run_patient_list_filter_four(request, campaign):
    try:
        timestamp_from = datetime.strptime(
            request.GET["date_filter_day"], "%Y-%m-%d"
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp_to = datetime.strptime(
            request.GET["date_filter_day"], "%Y-%m-%d"
        ).replace(hour=23, minute=59, second=59, microsecond=0)
        data = __run_timestamp_filter(campaign, timestamp_to, timestamp_from)
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
        data = __run_timestamp_filter(campaign, timestamp_to, timestamp_from)
    except ValueError:
        data = []
    return data


@silk_profile("--run-patient-list-filter")
def __run_patient_list_filter(request):
    current_campaign = Campaign.objects.get(name=request.user.current_campaign)
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
    return list(data)


@is_authenticated
@silk_profile("filter-patient-list-view")
def filter_patient_list_view(request):
    """
    Runs a search of all patients, using a name entered on the List page.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    data = __run_patient_list_filter(request)
    data = sorted(data, reverse=True, key=get_latest_timestamp)
    paginator = Paginator(data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "list/patient_filter.html",
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


@is_authenticated
@silk_profile("search-patient-list-view")
def search_patient_list_view(request):
    """
    Runs a search of all patients, using a name entered on the List page.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    try:
        current_campaign = Campaign.objects.get(name=request.user.current_campaign)
        patients = Patient.objects.filter(campaign=current_campaign)
        data = None
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
                            Q(first_name__icontains=term) | Q(last_name__icontains=term)
                        ),
                    )
                )
            )
        data = data if data is not None else []
    except ObjectDoesNotExist:
        data = []
    data = sorted(data, reverse=True, key=get_latest_timestamp)
    paginator = Paginator(data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "list/patient_search.html",
        {
            "user": request.user,
            "page_obj": page_obj,
            "name_search": request.GET.get("name_search")
            if request.GET.get("name_search") is not None
            else "",
            # pylint: disable=C0301
            "page_tip": "This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.",
        },
    )


def __parse_phone_number(input_string):
    if len(input_string) < 10 or len(input_string) > 10:
        return_response = input_string
    else:
        return_response = (
            f"({input_string[0:3]}){input_string[3:6]}-{input_string[6:10]}"
        )
    return return_response


@is_authenticated
def chief_complaint_list_view(request, patient_id=None, encounter_id=None):
    return render(
        request,
        "list/chief_complaint.html",
        {
            "list_view": ChiefComplaint.objects.filter(active=True),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "new": (encounter_id is None),
        },
    )
