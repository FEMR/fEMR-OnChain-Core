"""
Exports Patient and PatientEncounter information in CCDA format.
"""

from django.http import HttpResponse
from main.models import Patient, PatientEncounter


def __retrieve_patient_data():
    return list(Patient.objects.all())


def __retrieve_patient_encounter_data():
    return list(PatientEncounter.objects.all())


def __package_patient_data():
    patients = __retrieve_patient_data()


def __package_patient_encounter_data():
    encounters = __retrieve_patient_encounter_data()


def __package_xml_bundle():
    pass


def __prepare_file():
    pass


def ccda_export(request):
    return HttpResponse(__prepare_file(), content_type='text/json')
