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

from .models import PatientEncounter, Patient, Campaign


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
                       'list_view': data, 'page_name': 'Manager'})
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
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="patient_export.csv"'
        writer = csv.writer(resp)
        if units == 'i':
            writer.writerow(['Patient', 'Date Seen', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Mean Arterial Pressure', 'Heart Rate',
                             'Body Temperature (F)', 'Height (ft)', 'Weight (lbs)', 'BMI', 'Oxygen Concentration', 'Glucose Level'])
        else:
            writer.writerow(['Patient', 'Date Seen', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Mean Arterial Pressure',
                             'Heart Rate', 'Body Temperature (C)', 'Height (m)', 'Weight (kg)', 'BMI', 'Oxygen Concentration', 'Glucose Level'])
        try:
            data = Patient.objects.filter(
                campaign=Campaign.objects.get(name=request.session['campaign']))
        except ObjectDoesNotExist:
            data = list()
        id = 1
        for patient in data:
            for encounter in PatientEncounter.objects.filter(patient=patient):
                if units == 'i':
                    writer.writerow([id, encounter.timestamp, encounter.systolic_blood_pressure, encounter.diastolic_blood_pressure, encounter.mean_arterial_pressure, encounter.heart_rate,
                                     round(
                                         (encounter.body_temperature * 9/5) + 32, 2),
                                     "{0} {1}".format(
                                         math.floor(
                                             round((encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) // 12),
                                         round((encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) % 12),
                                     round(encounter.body_weight * 2.2046, 2),
                                     encounter.body_mass_index, encounter.oxygen_concentration, encounter.glucose_level])
                else:
                    writer.writerow([id, encounter.timestamp, encounter.systolic_blood_pressure, encounter.diastolic_blood_pressure, encounter.mean_arterial_pressure, encounter.heart_rate, encounter.body_temperature,
                                     "{0} {1}".format(
                                         encounter.body_height_primary, encounter.body_height_secondary), encounter.body_weight, encounter.body_mass_index, encounter.oxygen_concentration, encounter.glucose_level])
            id += 1
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
                       'list_view': data, 'page_name': 'Manager',
                       'selected': selected,
                       'filter_day': request.GET["date_filter_day"],
                       'filter_start': request.GET["date_filter_start"],
                       'filter_end': request.GET["date_filter_end"]})
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
                Q(first_name__icontains=request.GET['name_search']) |
                Q(last_name__icontains=request.GET['name_search']) |
                Q(phone_number__icontains=request.GET['name_search']) |
                Q(phone_number__icontains=__parse_phone_number(request.GET['name_search'])) |
                Q(email_address__icontains=request.GET['name_search'])
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
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def __parse_phone_number(input_string):
    if len(input_string) < 10 or len(input_string) > 10:
        return input_string
    else:
        return "({0}){1}-{2}".format(input_string[0:3], input_string[3:6], input_string[6:10])
