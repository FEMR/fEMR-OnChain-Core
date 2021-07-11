"""
View functions handling displaying data models as sortable, filterable lists.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
import itertools
import csv
from datetime import datetime, timedelta
import math

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from pytz import timezone as pytz_timezone

from .models import ChiefComplaint, PatientEncounter, Patient, Campaign, Treatment, Vitals


def get_latest_timestamp(patient):
    try:
        return PatientEncounter.objects.filter(patient=patient).order_by('-timestamp')[0].timestamp
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
            now = timezone.make_aware(
                datetime.today(), timezone.get_default_timezone())
            now = now.astimezone(timezone.get_current_timezone())
            data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(
                patientencounter__timestamp__date=now)
            data = set(list(itertools.chain(data, Patient.objects.filter(
                campaign=Campaign.objects.get(name=request.session['campaign'])).filter(timestamp__date=now))))
        except ObjectDoesNotExist:
            data = list()
        return render(request, 'list/patient.html',
                      {'user': request.user,
                       'list_view': sorted(data, reverse=True, key=get_latest_timestamp),
                       'page_name': 'Manager',
                       'page_tip': 'This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.'})
    else:
        return redirect('main:not_logged_in')


def patient_csv_export_view(request):
    """
    CSV Export of an Administrative/Clinician list of patients entered into the system.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        units = Campaign.objects.get(name=request.session['campaign']).units
        telehealth = Campaign.objects.get(
            name=request.session['campaign']).telehealth
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="patient_export.csv"'
        writer = csv.writer(resp)
        if units == 'i':
            title_row = ['Patient', 'Date Seen', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Mean Arterial Pressure', 'Heart Rate',
                         'Body Temperature (F)', 'Height', 'Weight (lbs)', 'BMI', 'Oxygen Concentration', 'Glucose Level', 'History of Tobacco Use',
                         'History of Diabetes', 'History of Hypertension', 'History of High Cholesterol',
                         'History of Alchol Abuse/Substance Abuse', 'Community Health Worker Notes', 'Procedure/Counseling', 'Pharmacy Notes',
                         'Medical/Surgical History', 'Social History', 'Current Medications', 'Family History']
        else:
            title_row = ['Patient', 'Date Seen', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Mean Arterial Pressure',
                         'Heart Rate', 'Body Temperature (C)', 'Height', 'Weight (kg)', 'BMI', 'Oxygen Concentration', 'Glucose Level',
                         'History of Tobacco Use', 'History of Diabetes', 'History of Hypertension', 'History of High Cholesterol',
                         'History of Alchol Abuse/Substance Abuse', 'Community Health Worker Notes', 'Procedure/Counseling', 'Pharmacy Notes',
                         'Medical/Surgical History', 'Socil History', 'Current Medications', 'Family History']
        try:
            data = Patient.objects.filter(
                campaign=Campaign.objects.get(name=request.session['campaign']))
        except ObjectDoesNotExist:
            data = list()
        id = 1
        time_zone = Campaign.objects.get(
            name=request.session['campaign']).timezone
        campaign_time_zone = pytz_timezone(time_zone)
        campaign_time_zone_b = datetime.now(
            tz=campaign_time_zone).strftime("%Z%z")
        patient_rows = list()
        max_treatments = 0
        for patient in data:
            for encounter in PatientEncounter.objects.filter(patient=patient):
                vital = Vitals.objects.filter(encounter=encounter)[0]
                if units == 'i':
                    row = [id,
                           "{} {}".format(encounter.timestamp.astimezone(
                               campaign_time_zone), campaign_time_zone_b),
                           vital.systolic_blood_pressure, vital.diastolic_blood_pressure,
                           vital.mean_arterial_pressure, vital.heart_rate,
                           round(
                                (vital.body_temperature * 9/5) + 32, 2),
                           "{0}' {1}\"".format(
                               math.floor(
                                   round((encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) // 12),
                               round((encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) % 12),
                           round(encounter.body_weight * 2.2046, 2),
                           encounter.body_mass_index, vital.oxygen_concentration, vital.glucose_level, encounter.smoking,
                           encounter.history_of_diabetes, encounter.history_of_hypertension, encounter.history_of_high_cholesterol,
                           encounter.alcohol, encounter.community_health_worker_notes, encounter.procedure, encounter.pharmacy_notes,
                           encounter.medical_history, encounter.social_history, encounter.current_medications, encounter.family_history]
                else:
                    row = [id,
                           "{} {}".format(encounter.timestamp.astimezone(
                               campaign_time_zone), campaign_time_zone_b),
                           vital.systolic_blood_pressure, vital.diastolic_blood_pressure,
                           vital.mean_arterial_pressure, vital.heart_rate, vital.body_temperature,
                           "{0} m {1} cm".format(
                               encounter.body_height_primary, encounter.body_height_secondary), encounter.body_weight,
                           encounter.body_mass_index, vital.oxygen_concentration, vital.glucose_level, encounter.smoking,
                           encounter.history_of_diabetes, encounter.history_of_hypertension, encounter.history_of_high_cholesterol,
                           encounter.alcohol, encounter.community_health_worker_notes, encounter.procedure, encounter.pharmacy_notes,
                           encounter.medical_history, encounter.social_history, encounter.current_medications, encounter.family_history]
                treatments = Treatment.objects.filter(encounter=encounter)
                max_treatments = len(treatments) if len(treatments) > max_treatments else max_treatments
                for x in treatments:
                    row.extend([x.diagnosis, x.medication, x.administration_schedule, x.days, x.prescriber])
                patient_rows.append(row)
            id += 1
        for x in range(max_treatments):
            title_row.extend(['Diagnosis', 'Medication', 'Administration Schedule', 'Days', 'Prescriber'])
        writer.writerow(title_row)
        for row in patient_rows:
            writer.writerow(row)
        return resp
    else:
        return redirect('main:not_logged_in')


def filter_patient_list_view(request):
    """
    Runs a search of all patients, using a name entered on the List page.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        selected = 1
        try:
            if request.GET["filter_list"] == "1":
                now = timezone.make_aware(
                    datetime.today(), timezone.get_default_timezone())
                now = now.astimezone(timezone.get_current_timezone())
                data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(
                    patientencounter__timestamp__date=now)
                data = set(list(itertools.chain(data, Patient.objects.filter(
                    campaign=Campaign.objects.get(name=request.session['campaign'])).filter(timestamp__date=now))))
                selected = 1
            elif request.GET["filter_list"] == "2":
                timestamp_from = timezone.now() - timedelta(days=7)
                timestamp_to = timezone.now()
                data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(patientencounter__timestamp__gte=timestamp_from,
                                                                                                                      patientencounter__timestamp__lt=timestamp_to)
                data = set(list(itertools.chain(data, Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(timestamp__gte=timestamp_from,
                                                                                                                                                     timestamp__lt=timestamp_to))))
                selected = 2
            elif request.GET["filter_list"] == "3":
                timestamp_from = timezone.now() - timedelta(days=30)
                timestamp_to = timezone.now()
                data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(patientencounter__timestamp__gte=timestamp_from,
                                                                                                                      patientencounter__timestamp__lt=timestamp_to)
                data = set(list(itertools.chain(data, Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(timestamp__gte=timestamp_from,
                                                                                                                                                     timestamp__lt=timestamp_to))))
                selected = 3
            elif request.GET["filter_list"] == "4":
                try:
                    timestamp_from = datetime.strptime(
                        request.GET["date_filter_day"], "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
                    timestamp_to = datetime.strptime(
                        request.GET["date_filter_day"], "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=0)
                    data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(patientencounter__timestamp__gte=timestamp_from,
                                                                                                                          patientencounter__timestamp__lt=timestamp_to)
                    data = set(list(itertools.chain(data, Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(timestamp__gte=timestamp_from,
                                                                                                                                                         timestamp__lt=timestamp_to))))
                except ValueError:
                    data = list()
                selected = 4
            elif request.GET["filter_list"] == "5":
                try:
                    timestamp_from = datetime.strptime(
                        request.GET["date_filter_start"], "%Y-%m-%d")
                    timestamp_to = datetime.strptime(
                        request.GET["date_filter_end"], "%Y-%m-%d") + timedelta(days=1)
                    data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(patientencounter__timestamp__gte=timestamp_from,
                                                                                                                          patientencounter__timestamp__lt=timestamp_to)
                    data = set(list(itertools.chain(data, Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(timestamp__gte=timestamp_from,
                                                                                                                                                         timestamp__lt=timestamp_to))))
                except ValueError:
                    data = list()
                selected = 5
            elif request.GET["filter_list"] == "6":
                try:
                    data = Patient.objects.filter(
                        campaign=Campaign.objects.get(name=request.session['campaign']))
                except ValueError:
                    data = list()
                selected = 6
            else:
                data = list()
        except ObjectDoesNotExist:
            data = list()
        return render(request, 'list/patient.html',
                      {'user': request.user,
                       'list_view': sorted(data, reverse=True, key=get_latest_timestamp),
                       'page_name': 'Manager',
                       'selected': selected,
                       'filter_day': request.GET["date_filter_day"],
                       'filter_start': request.GET["date_filter_start"],
                       'filter_end': request.GET["date_filter_end"],
                       'page_tip': 'This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.'})
    else:
        return redirect('main:not_logged_in')


def search_patient_list_view(request):
    """
    Runs a search of all patients, using a name entered on the List page.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        try:
            data = Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(
                Q(campaign_key__icontains=request.GET['name_search']) |
                Q(first_name__icontains=request.GET['name_search']) |
                Q(last_name__icontains=request.GET['name_search']) |
                Q(phone_number__icontains=request.GET['name_search']) |
                Q(phone_number__icontains=__parse_phone_number(request.GET['name_search'])) |
                Q(email_address__iexact=request.GET['name_search'])
            )
            for term in request.GET['name_search'].split():
                data = set(list(itertools.chain(data, Patient.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign'])).filter(
                    Q(first_name__icontains=term) |
                    Q(last_name__icontains=term)
                ))))
        except ObjectDoesNotExist:
            data = list()
        return render(request, 'list/patient.html',
                      {'user': request.user,
                       'list_view': sorted(data, reverse=True, key=get_latest_timestamp),
                       'page_tip': 'This provides an overview of all patients in a campaign or location seen that day, week, month, etc. Campaign is listed at the top of the page.'})
    else:
        return redirect('main:not_logged_in')


def __parse_phone_number(input_string):
    if len(input_string) < 10 or len(input_string) > 10:
        return input_string
    else:
        return "({0}){1}-{2}".format(input_string[0:3], input_string[3:6], input_string[6:10])


def chief_complaint_list_view(request, patient_id=None, encounter_id=None):
    if request.user.is_authenticated:
        return render(request, 'list/chief_complaint.html', {
            'list_view': ChiefComplaint.objects.filter(active=True),
            'patient_id': patient_id,
            'encounter_id': encounter_id,
            'new': (encounter_id is None)
        })
    else:
        return redirect('main:not_logged_in')
