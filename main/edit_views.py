"""
Handles template rendering and logic for editing web forms.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from main.femr_admin_views import get_client_ip
import math
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AllergyForm, ImmunizationForm, ProblemForm, ProcedureForm, MedicationForm, LabTestForm, TestForm, \
    PatientForm, HealthConcernForm, PatientEncounterForm
from .models import Allergy, Campaign, Immunization, Problem, Procedure, Medication, HealthConcern, Patient, Test, LabTest, \
    PatientEncounter, DatabaseChangeLog
from main.qldb_interface import update_patient, update_patient_encounter


def allergy_edit_form_view(request, id=None):
    """
    Used to edit Allergy objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HttpResponse rendering forms/allergy.html.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = AllergyForm(request.POST or None,
                               instance=Allergy.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = AllergyForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(Allergy, pk=id)
            form = AllergyForm(instance=m)
        return render(request, 'forms/allergy.html', {'error': error,
                                                      'form': form})
    else:
        return redirect('/not_logged_in')


def immunization_edit_form_view(request, id=None):
    """
    Used to edit Immunization objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = ImmunizationForm(request.POST or None,
                                    instance=Immunization.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = ImmunizationForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(Immunization, pk=id)
            form = ImmunizationForm(instance=m)
        return render(request, 'forms/allergy.html', {'error': error,
                                                      'form': form})
    else:
        return redirect('/not_logged_in')


def problem_edit_form_view(request, id=None):
    """
    Used to edit Problem objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = ProblemForm(request.POST or None,
                               instance=Problem.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = ProblemForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(Problem, pk=id)
            form = ProblemForm(instance=m)
        return render(request, 'forms/problem.html', {'error': error,
                                                      'form': form})
    else:
        return redirect('/not_logged_in')


def procedure_edit_form_view(request, id=None):
    """
    Used to edit Procedure objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = ProcedureForm(request.POST or None,
                                 instance=Procedure.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = ProcedureForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(Procedure, pk=id)
            form = ProcedureForm(instance=m)
        return render(request, 'forms/procedure.html', {'error': error,
                                                        'form': form})
    else:
        return redirect('/not_logged_in')


def medication_edit_form_view(request, id=None):
    """
    Used to edit Medication objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = MedicationForm(request.POST or None,
                                  instance=Medication.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = MedicationForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(Medication, pk=id)
            form = MedicationForm(instance=m)
        return render(request, 'forms/medication.html', {'error': error,
                                                         'form': form})
    else:
        return redirect('/not_logged_in')


def lab_test_edit_form_view(request, id=None):
    """
    Used to edit LabTest objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = LabTestForm(request.POST or None,
                               instance=LabTest.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = LabTestForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(LabTest, pk=id)
            form = LabTestForm(instance=m)
        return render(request, 'forms/lab_test.html', {'error': error,
                                                       'form': form})
    else:
        return redirect('/not_logged_in')


def test_edit_form_view(request, id=None):
    """
    Used to edit Test objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = TestForm(request.POST or None,
                            instance=Test.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = TestForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(Test, pk=id)
            form = TestForm(instance=m)
        return render(request, 'forms/test.html', {'error': error,
                                                   'form': form})
    else:
        return redirect('/not_logged_in')


def patient_edit_form_view(request, id=None):
    """
    Used to edit Patient objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        error = ""
        m = get_object_or_404(Patient, pk=id)
        encounters = PatientEncounter.objects.filter(patient=m)
        if request.method == 'POST':
            form = PatientForm(request.POST or None,
                               instance=m)
            if form.is_valid():
                t = form.save()
                t.campaign.add(Campaign.objects.get(
                    name=request.session['campaign']))
                t.save()
                DatabaseChangeLog.objects.create(action="Edit", model="Patient", instance=str(t),
                                                 ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                update_patient(form.cleaned_data)
                form = PatientForm()
                error = "Form submitted successfully."
                return render(request, "data/patient_submitted.html", {'patient_id': t.id})
            else:
                error = "Form is invalid."
        else:
            DatabaseChangeLog.objects.create(action="View", model="Patient", instance=str(m),
                                             ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
            form = PatientForm(instance=m)
        return render(request, 'forms/patient.html', {'error': error, 'patient_id': id, 'encounters': encounters,
                                                      'form': form, 'page_name': 'Returning Patient'})
    else:
        return redirect('/not_logged_in')


def encounter_edit_form_view(request, patient_id=None, encounter_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        units = Campaign.objects.get(name=request.session['campaign']).units
        m = get_object_or_404(PatientEncounter, pk=encounter_id)
        p = get_object_or_404(Patient, pk=patient_id)
        if request.method == 'POST':
            form = PatientEncounterForm(request.POST or None,
                                        instance=m, unit=units)
            if form.is_valid():
                encounter = form.save(commit=False)
                encounter.patient = p
                encounter.save()
                DatabaseChangeLog.objects.create(action="Edit", model="PatientEncounter", instance=str(encounter),
                                                 ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                update_patient_encounter(form.cleaned_data)
                if 'submit_encounter' in request.POST:
                    return render(request, 'data/encounter_submitted.html')
                elif 'submit_refer' in request.POST:
                    kwargs = {"id": patient_id}
                    return redirect('main:referral_form_view', **kwargs)
                else:
                    return render(request, 'data/encounter_submitted.html')
        else:
            DatabaseChangeLog.objects.create(action="View", model="Patient", instance=str(m),
                                             ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
            form = PatientEncounterForm(
                instance=m, unit=units)
            if units == 'i':
                form.initial = {
                    'systolic_blood_pressure': m.systolic_blood_pressure,
                    'diastolic_blood_pressure': m.diastolic_blood_pressure,
                    'heart_rate': m.heart_rate,
                    'oxygen_concentration': m.oxygen_concentration,
                    'glucose_level': m.glucose_level,
                    'body_mass_index': m.body_mass_index,
                    'mean_arterial_pressure': m.mean_arterial_pressure,
                    'smoking': m.smoking,
                    'history_of_diabetes': m.history_of_diabetes,
                    'history_of_hypertension': m.history_of_hypertension,
                    'history_of_high_cholesterol': m.history_of_high_cholesterol,
                    'alcohol': m.alcohol,
                    'community_health_worker_notes': m.community_health_worker_notes,
                    'body_height_primary': math.floor(
                        ((m.body_height_primary * 100 + m.body_height_secondary) / 2.54) // 12),
                    'body_height_secondary': round((
                        (m.body_height_primary * 100 + m.body_height_secondary) / 2.54) % 12, 2),
                    'body_weight': round(m.body_weight * 2.2046, 2),
                    'body_temperature': round((
                        m.body_temperature * 9/5) + 32, 2)
                }
        suffix = p.get_suffix_display() if p.suffix is not None else ""
        return render(request, 'forms/edit_encounter.html',
                      {'form': form, 'page_name': 'Edit Encounter for {} {} {}'.format(p.first_name, p.last_name, suffix),
                       'birth_sex': p.sex_assigned_at_birth, 'patient_id': patient_id, 'encounter_id': encounter_id,
                       'patient_name': "{} {} {}".format(p.first_name, p.last_name, suffix), 'units': units})
    else:
        return redirect('/not_logged_in')


def health_concern_edit_form_view(request, id=None):
    """
    Used to edit HealthConcern objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        error = ""
        if request.method == 'POST':
            form = HealthConcernForm(request.POST or None,
                                     instance=HealthConcern.objects.get(id=id))
            if form.is_valid():
                t = form.save()
                t.save()
                form = HealthConcernForm()
                error = "Form submitted successfully."
            else:
                error = "Form is invalid."
        else:
            m = get_object_or_404(HealthConcern, pk=id)
            form = HealthConcernForm(instance=m)
        return render(request, 'forms/health_concern.html', {'error': error,
                                                             'form': form})
    else:
        return redirect('/not_logged_in')


def patient_export_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        m = get_object_or_404(Patient, pk=id)
        encounters = PatientEncounter.objects.filter(patient=m).order_by('-timestamp')
        if request.method == 'GET':
            return render(request, 'export/patient_export.html', {
                'patient': m,
                'encounters': encounters,
                'units': Campaign.objects.get(name=request.session['campaign']).units
            })
    else:
        return redirect('/not_logged_in')
