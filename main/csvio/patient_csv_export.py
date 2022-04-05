"""
This file contains a single function which handles exporting
patient records as CSV files.
"""
import csv
from datetime import datetime
import math
from silk.profiling.profiler import silk_profile
from pytz import timezone as pytz_timezone
from django.http.response import HttpResponse
from main.models import (
    Campaign,
    HistoryOfPresentIllness,
    Patient,
    PatientEncounter,
    Treatment,
    Vitals,
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


@silk_profile("extend-vitals-list")
def extend_vitals_list(campaign, vitals, row):
    for vital in vitals:
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


# pylint: disable=R0914
@silk_profile("run-patient-csv-export")
def run_patient_csv_export(request):
    campaign = Campaign.objects.get(name=request.session["campaign"])
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="patient_export.csv"'
    writer = csv.writer(resp)
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
    patient_data = Patient.objects.filter(campaign=campaign)
    export_id = 1
    campaign_time_zone = pytz_timezone(campaign.timezone)
    campaign_time_zone_b = datetime.now(tz=campaign_time_zone).strftime("%Z%z")
    patient_rows = []
    max_treatments = 0
    max_hpis = 0
    max_vitals = 0
    vitals_dict = {}
    treatments_dict = {}
    hpis_dict = {}
    all_vitals = Vitals.objects.all()
    all_treatments = Treatment.objects.all()
    all_hpis = HistoryOfPresentIllness.objects.all()
    for patient in patient_data:
        for encounter in patient.patientencounter_set.all():
            vitals = all_vitals.filter(encounter=encounter)
            treatments = all_treatments.filter(encounter=encounter)
            hpis = all_hpis.filter(encounter=encounter)

            vitals_dict[encounter] = vitals
            treatments_dict[encounter] = treatments
            hpis_dict[encounter] = hpis

            max_treatments = max(len(treatments), max_treatments)
            max_hpis = max(len(hpis), max_hpis)
            max_vitals = max(len(vitals), max_vitals)
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
            vitals = vitals_dict[encounter]
            treatments = treatments_dict[encounter]
            hpis = hpis_dict[encounter]
            extend_vitals_list(campaign, vitals, row)
            if len(vitals) < max_vitals:
                row.extend(["", "", "", "", "", "", ""] * (max_vitals - len(vitals)))
            for item in treatments:
                row.extend(
                    [
                        item.diagnosis,
                        ",".join([str(x) for x in item.medication.all()]),
                        item.administration_schedule,
                        item.days,
                        item.prescriber,
                    ]
                )
            if len(treatments) < max_treatments:
                row.extend(["", "", "", "", ""] * (max_treatments - len(treatments)))
            for item in hpis:
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
            if len(hpis) < max_hpis:
                row.extend(
                    ["", "", "", "", "", "", "", "", "", "", ""]
                    * (max_hpis - len(hpis))
                )
            patient_rows.append(row)
        export_id += 1
    build_title_row(campaign, title_row, max_vitals, max_treatments, max_hpis)
    writer.writerow(title_row)
    for row in patient_rows:
        writer.writerow(row)
    return resp
