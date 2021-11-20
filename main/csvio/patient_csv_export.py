"""
This file contains a single function which handles exporting
patient records as CSV files.
"""
import csv
from datetime import datetime
import math
from pytz import timezone as pytz_timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from main.models import Campaign, Patient, PatientEncounter, Treatment, Vitals


# pylint: disable=R0914
def run_patient_csv_export(request):
    campaign = Campaign.objects.get(name=request.session["campaign"])
    units = campaign.units
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="patient_export.csv"'
    writer = csv.writer(resp)
    title_row = [
        "Patient",
        "Date Seen",
        "Systolic Blood Pressure",
        "Diastolic Blood Pressure",
        "Mean Arterial Pressure",
        "Heart Rate",
        "Body Temperature (F)" if units == "i" else "Body Temperature (C)",
        "Height",
        "Weight (lbs)" if units == "i" else "Weight (kg)",
        "BMI",
        "Oxygen Concentration",
        "Glucose Level",
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
    try:
        data = Patient.objects.filter(campaign=campaign).exclude(
            Q(first_name__icontains="test")
            | Q(last_name__icontains="test")
            | Q(middle_name__icontains="test")
            | Q(city__icontains="test")
        )
    except ObjectDoesNotExist:
        data = []
    export_id = 1
    campaign_time_zone = pytz_timezone(campaign.timezone)
    campaign_time_zone_b = datetime.now(tz=campaign_time_zone).strftime("%Z%z")
    patient_rows = []
    max_treatments = 0
    for patient in data:
        for encounter in PatientEncounter.objects.filter(patient=patient):
            vital = Vitals.objects.filter(encounter=encounter)[0]
            row = [
                export_id,
                # pylint: disable=C0301
                f"{encounter.timestamp.astimezone(campaign_time_zone)} {campaign_time_zone_b}",
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
                vital.oxygen_concentration,
                vital.glucose_level,
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
            treatments = Treatment.objects.filter(encounter=encounter)
            max_treatments = (
                len(treatments) if len(treatments) > max_treatments else max_treatments
            )
            for item in treatments:
                row.extend(
                    [
                        item.diagnosis,
                        item.medication,
                        item.administration_schedule,
                        item.days,
                        item.prescriber,
                    ]
                )
            patient_rows.append(row)
        export_id += 1
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
    writer.writerow(title_row)
    for row in patient_rows:
        writer.writerow(row)
    return resp
