"""
This file contains a single function which handles exporting
patient records as CSV files.
"""
import csv
from datetime import datetime
import math
from pytz import timezone as pytz_timezone
from django.http.response import HttpResponse
from main.models import (
    Campaign,
    HistoryOfPresentIllness,
    Patient,
    Treatment,
    Vitals,
)


# pylint: disable=R0914
def run_patient_csv_export(request):
    campaign = Campaign.objects.get(name=request.session["campaign"])
    units = campaign.units
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="patient_export.csv"'
    writer = csv.writer(resp)
    title_row = [
        "Patient",
        "Sex Assigned at Birth",
        "Age (years)",
        "Date Seen",
        "Height",
        "Weight (lbs)" if units == "i" else "Weight (kg)",
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
    data = Patient.objects.filter(campaign=campaign)
    export_id = 1
    campaign_time_zone = pytz_timezone(campaign.timezone)
    campaign_time_zone_b = datetime.now(tz=campaign_time_zone).strftime("%Z%z")
    patient_rows = []
    max_treatments = 0
    max_hpis = 0
    max_vitals = 0
    for patient in data:
        for encounter in patient.patientencounter_set.all():
            row = [
                export_id,
                patient.sex_assigned_at_birth,
                patient.age,
                # pylint: disable=C0301
                f"{encounter.timestamp.astimezone(campaign_time_zone)} {campaign_time_zone_b}",
                # pylint: disable=C0209
                "{0}' {1}\"".format(
                    math.floor(
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
                    ),
                    round(
                        (
                            encounter.body_height_primary * 100
                            + encounter.body_height_secondary
                        )
                        / 2.54
                    )
                    % 12,
                )
                if units == "i"
                else f"{encounter.body_height_primary} m {encounter.body_height_secondary} cm",
                round(
                    (encounter.body_weight if encounter.body_weight is not None else 0)
                    * 2.2046,
                    2,
                )
                if units == "i"
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
            vitals = Vitals.objects.filter(encounter=encounter)
            treatments = Treatment.objects.filter(encounter=encounter)
            hpis = HistoryOfPresentIllness.objects.filter(encounter=encounter)
            max_treatments = max(len(treatments), max_treatments)
            max_hpis = max(len(hpis), max_hpis)
            max_vitals = max(len(vitals), max_vitals)
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
                        if units == "i"
                        else vital.body_temperature,
                        vital.oxygen_concentration,
                        vital.glucose_level,
                    ]
                )
                if len(vitals) < max_vitals:
                    row.extend([""] * (max_vitals - len(vitals)))
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
                    row.extend([""] * (max_treatments - len(treatments)))
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
                    row.extend([""] * (max_hpis - len(hpis)))
            patient_rows.append(row)
        export_id += 1
    for _ in range(max_vitals):
        title_row.extend(
            [
                "Systolic Blood Pressure",
                "Diastolic Blood Pressure",
                "Mean Arterial Pressure",
                "Heart Rate",
                "Body Temperature (F)" if units == "i" else "Body Temperature (C)",
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
    writer.writerow(title_row)
    for row in patient_rows:
        writer.writerow(row)
    return resp
