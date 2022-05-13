"""
This file contains a single function which handles exporting
patient records as CSV files.
"""
import csv
from io import StringIO
import math
import os
from datetime import datetime, timedelta

from celery import shared_task
from silk.profiling.profiler import silk_profile
from pytz import timezone as pytz_timezone

from django.http.response import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from clinic_messages.models import Message

from main.background_tasks import check_admin_permission
from main.models import (
    CSVExport,
    Campaign,
    Patient,
    PatientEncounter,
    fEMRUser,
)


@silk_profile("calc-height")
def calc_height(encounter: PatientEncounter) -> str:
    primary = math.floor(
        round(
            (
                (
                    encounter.body_height_primary
                    if encounter.body_height_primary is not None
                    else 0
                )
                * 100
                + (
                    encounter.body_height_secondary
                    if encounter.body_height_secondary is not None
                    else 0
                )
            )
            / 2.54
        )
        // 12
    )
    secondary = (
        round(
            (
                (
                    encounter.body_height_primary
                    if encounter.body_height_primary is not None
                    else 0
                )
                * 100
                + (
                    encounter.body_height_secondary
                    if encounter.body_height_secondary is not None
                    else 0
                )
            )
            / 2.54
        )
        % 12
    )
    return f"{primary}' {secondary}\""


@silk_profile("dict-builder")
def dict_builder(patient_data, vitals_dict, treatments_dict, hpis_dict):
    max_treatments = 0
    max_hpis = 0
    max_vitals = 0
    for patient in patient_data:
        for encounter in patient.patientencounter_set.all():
            vitals = encounter.vitals_set.all()
            vitals_count = vitals.count()
            treatments = encounter.treatment_set.all()
            treatments_count = treatments.count()
            hpis = encounter.historyofpresentillness_set.all()
            hpis_count = hpis.count()

            vitals_dict[encounter] = (vitals, vitals_count)
            treatments_dict[encounter] = (treatments, treatments_count)
            hpis_dict[encounter] = (hpis, hpis_count)

            max_treatments = max(treatments_count, max_treatments)
            max_hpis = max(hpis_count, max_hpis)
            max_vitals = max(vitals_count, max_vitals)
    return max_treatments, max_hpis, max_vitals


@silk_profile("extend-vitals-list")
def extend_vitals_list(campaign, vitals, row, max_vitals):
    for vital in vitals[0]:
        row.extend(
            [
                vital.systolic_blood_pressure,
                vital.diastolic_blood_pressure,
                vital.mean_arterial_pressure,
                vital.heart_rate,
                round(
                    (
                        (
                            vital.body_temperature
                            if vital.body_temperature is not None
                            else 0
                        )
                        * 9
                        / 5
                    )
                    + 32,
                    2,
                )
                if campaign.units == "i"
                else vital.body_temperature,
                vital.oxygen_concentration,
                vital.glucose_level,
            ]
        )
    if vitals[1] < max_vitals:
        row.extend(["", "", "", "", "", "", ""] * (max_vitals - vitals[1]))


@silk_profile("extend-treatments-list")
def extend_treatments_list(row, treatments, max_treatments):
    for item in treatments[0]:
        row.extend(
            [
                item.diagnosis,
                ",".join([str(x) for x in item.medication.all()]),
                item.administration_schedule,
                item.days,
                item.prescriber,
            ]
        )
    if treatments[1] < max_treatments:
        row.extend(["", "", "", "", ""] * (max_treatments - treatments[1]))


@silk_profile("extend-hpis-list")
def extend_hpis_list(row, hpis, max_hpis):
    for item in hpis[0]:
        row.extend(
            [
                item.chief_complaint,
                item.onset,
                item.provokes,
                item.palliates,
                item.quality,
                item.radiation,
                item.severity,
                item.time_of_day,
                item.narrative,
                item.physical_examination,
                item.tests_ordered,
            ]
        )
    if hpis[1] < max_hpis:
        row.extend(["", "", "", "", "", "", "", "", "", "", ""] * (max_hpis - hpis[1]))


@silk_profile("build-title-row")
def build_title_row(campaign, title_row, max_vitals, max_treatments, max_hpis):
    for _ in range(max_vitals):
        title_row.extend(
            [
                "Systolic Blood Pressure",
                "Diastolic Blood Pressure",
                "Mean Arterial Pressure",
                "Heart Rate",
                "Body Temperature (F)"
                if campaign.units == "i"
                else "Body Temperature (C)",
                "Oxygen Concentration",
                "Glucose Level",
            ]
        )
    for _ in range(max_treatments):
        title_row.extend(
            [
                "Diagnosis",
                "Medication",
                "Administration Schedule",
                "Days",
                "Prescriber",
            ]
        )
    for _ in range(max_hpis):
        title_row.extend(
            [
                "Chief Complaint",
                "Onset",
                "Provokes",
                "Palliates",
                "Quality",
                "Radiation",
                "Severity",
                "Time of Day",
                "Narrative",
                "Physical Examination",
                "Tests Ordered",
            ]
        )


@silk_profile("write-result-file")
def write_result_file(writer, title_row, patient_rows):
    writer.writerow(title_row)
    for row in patient_rows:
        writer.writerow(row)


def patient_processing_loop(
    patient_data,
    patient_rows,
    campaign,
    vitals_dict,
    max_vitals,
    treatments_dict,
    max_treatments,
    hpis_dict,
    max_hpis,
):
    campaign_time_zone = pytz_timezone(campaign.timezone)
    campaign_time_zone_b = datetime.now(tz=campaign_time_zone).strftime("%Z%z")
    export_id = 1
    for patient in patient_data:
        for encounter in patient.patientencounter_set.all():
            row = [
                export_id,
                patient.sex_assigned_at_birth,
                patient.age,
                patient.city,
                # pylint: disable=C0301
                f"{encounter.timestamp.astimezone(campaign_time_zone)} {campaign_time_zone_b}",
                calc_height(encounter)
                if campaign.units == "i"
                else f"{encounter.body_height_primary} m {encounter.body_height_secondary} cm",
                round(
                    (encounter.body_weight if encounter.body_weight is not None else 0)
                    * 2.2046,
                    2,
                )
                if campaign.units == "i"
                else encounter.body_weight,
                encounter.body_mass_index,
                encounter.smoking,
                encounter.history_of_diabetes,
                encounter.history_of_hypertension,
                encounter.history_of_high_cholesterol,
                encounter.alcohol,
                encounter.community_health_worker_notes,
                encounter.procedure,
                encounter.pharmacy_notes,
                encounter.medical_history,
                encounter.social_history,
                encounter.current_medications,
                encounter.family_history,
            ]
            extend_vitals_list(campaign, vitals_dict[encounter], row, max_vitals)
            extend_treatments_list(row, treatments_dict[encounter], max_treatments)
            extend_hpis_list(row, hpis_dict[encounter], max_hpis)
            patient_rows.append(row)
        export_id += 1
    return len(patient_rows)


@silk_profile("--filter-patients-by-week")
def __filter_patients_by_week(campaign):
    timestamp_from = timezone.now() - timedelta(days=7)
    timestamp_to = timezone.now()
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


@silk_profile("--filter-patients-by-month")
def __filter_patients_by_month(campaign):
    timestamp_from = timezone.now() - timedelta(days=30)
    timestamp_to = timezone.now()
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


@shared_task
@silk_profile("csv-export-handler")
def csv_export_handler(user_id, campaign_id, timeframe):
    campaign = Campaign.objects.get(pk=campaign_id)
    export_file = StringIO()
    writer = csv.writer(export_file)
    title_row = [
        "Patient",
        "Sex Assigned at Birth",
        "Age (years)",
        "City",
        "Date Seen",
        "Height",
        "Weight (lbs)" if campaign.units == "i" else "Weight (kg)",
        "BMI",
        "History of Tobacco Use",
        "History of Diabetes",
        "History of Hypertension",
        "History of High Cholesterol",
        "History of Alcohol Abuse/Substance Abuse",
        "Community Health Worker Notes",
        "Procedure/Counseling",
        "Pharmacy Notes",
        "Medical/Surgical History",
        "Social History",
        "Current Medications",
        "Family History",
    ]
    if timeframe == 2:
        patient_data = __filter_patients_by_week(campaign)
    elif timeframe == 3:
        patient_data = __filter_patients_by_month(campaign)
    else:
        patient_data = Patient.objects.filter(campaign=campaign)
    patient_rows = []
    vitals_dict = {}
    treatments_dict = {}
    hpis_dict = {}
    max_treatments, max_hpis, max_vitals = dict_builder(
        patient_data, vitals_dict, treatments_dict, hpis_dict
    )
    patient_processing_loop(
        patient_data,
        patient_rows,
        campaign,
        vitals_dict,
        max_vitals,
        treatments_dict,
        max_treatments,
        hpis_dict,
        max_hpis,
    )
    build_title_row(campaign, title_row, max_vitals, max_treatments, max_hpis)
    write_result_file(writer, title_row, patient_rows)
    user = fEMRUser.objects.get(pk=user_id)
    export = CSVExport()
    export.file.save(
        f"patient-export-{campaign.name}-{datetime.now()}.csv",
        ContentFile(export_file.getvalue().encode("utf-8")),
    )
    export.user = user
    export.campaign = campaign
    export.save()
    message = Message.objects.create(
        subject="CSV Export Finished",
        content="""
        This message is to let you know that the CSV export you began has finished. You can go back to the View Finished Exports page to download it.
        """,
        sender=fEMRUser.objects.get(username="admin"),
        recipient=user,
    )
    if os.environ.get("DEFAULT_FROM_EMAIL", None) is not None:
        send_mail(
            f"Message from {message.sender}",
            # pylint: disable=C0301
            f"{message.content}\n\n\nTHIS IS AN AUTOMATED MESSAGE. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO REPLY.",
            os.environ.get("DEFAULT_FROM_EMAIL"),
            [message.recipient.email],
        )


@silk_profile("csv-export-list")
def csv_export_list(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            exports = CSVExport.objects.filter(user=request.user).order_by("-id")
            paginator = Paginator(exports, 10)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)
            return_response = render(
                request, "admin/export_list.html", {"exports": page_obj}
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


@silk_profile("fetch-csv-export")
def fetch_csv_export(request, export_id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            export = CSVExport.objects.get(pk=export_id)
            with open(export.file.url, "rb") as file_handle:
                resp = HttpResponse(file_handle.read(), content_type="text/csv")
                resp[
                    "Content-Disposition"
                ] = f'attachment; filename="{os.path.basename(export.file.path)}"'
                return resp
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


@silk_profile("run-patient-csv-export")
def run_patient_csv_export(request, timeframe=1):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            campaign = Campaign.objects.get(name=request.user.current_campaign)
            csv_export_handler.delay(request.user.pk, campaign.id, timeframe)
            messages.info(
                request,
                "We're building your CSV - you'll receive a message once it's done. This may take up to 10 minutes.",
            )
            return_response = render(
                request, "admin/home.html", {"user": request.user, "page_name": "Admin"}
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
