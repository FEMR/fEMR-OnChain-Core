"""
Handles template rendering and logic for web forms.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
import math
import os
from datetime import datetime

from django.shortcuts import render, redirect

from main.femr_admin_views import get_client_ip
from .forms import DiagnosisForm, PatientForm, PatientEncounterForm, TreatmentForm, VitalsForm
from .models import Campaign, Patient, DatabaseChangeLog, PatientEncounter, cal_key
from .qldb_interface import create_new_patient, create_new_patient_encounter, update_patient_encounter


def patient_form_view(request):
    """
    Used to create new Patient objects.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        c = Campaign.objects.get(name=request.session['campaign'])
        ssn_error = False
        phone_error = False
        email_error = False
        shared_phone_error = False
        shared_email_error = False
        match = None
        if request.method == "POST":
            form = PatientForm(request.POST)
            if form.is_valid():
                t = form.save()
                t.campaign.add(c)
                key = None
                while key is None:
                    key = cal_key(c)
                t.campaign_key = key
                t.save()
                if os.environ.get('QLDB_ENABLED') == "TRUE":
                    create_new_patient(form.cleaned_data)
                DatabaseChangeLog.objects.create(action="Create", model="Patient", instance=str(t),
                                                 ip=get_client_ip(request), username=request.user.username,
                                                 campaign=Campaign.objects.get(name=request.session['campaign']))
                if t.id != '' and t.id is not None:
                    return render(request, "data/patient_submitted.html", {'patient': t, 'encounters': list()})
                else:
                    return render(request, "data/patient_not_submitted.html")
            else:
                if 'social_security_number' in form.errors and 'Must be 4 or 9 digits' not in \
                        form.errors['social_security_number'][0]:
                    ssn_error = True
                    match = Patient.objects.get(
                        social_security_number=form.data['social_security_number'])
                if 'phone_number' in form.errors:
                    phone_error = True
                    match = Patient.objects.filter(
                        phone_number=form.data['phone_number'])
                if 'email_address' in form.errors:
                    email_error = True
                    match = Patient.objects.filter(
                        email_address=form.data['email_address'])
        else:
            form = PatientForm()
        form.fields['race'].queryset = c.race_options
        form.fields['ethnicity'].queryset = c.ethnicity_options
        return render(request, 'forms/new_patient.html', {'ssn_error': ssn_error,
                                                          'phone_error': phone_error,
                                                          'email_error': email_error,
                                                          'shared_phone_error': shared_phone_error,
                                                          'shared_email_error': shared_email_error,
                                                          'match_list': match,
                                                          'form': form,
                                                          'page_name': 'New Patient',
                                                          'page_tip': "Complete form with patient demographics as instructed. Any box with an asterisk (*) is required. Shared contact information would be if two patients have a household phone or email that they share, for example."})
    else:
        return redirect('/not_logged_in')


def patient_encounter_form_view(request, id=None):
    """
    Used to create new PatientEncounter objects.

    :param request: Django Request object.
    :param id:
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        p = Patient.objects.get(pk=id)
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        telehealth = Campaign.objects.get(
            name=request.session['campaign']).telehealth
        treatment_form = TreatmentForm()
        diagnosis_form = DiagnosisForm()
        if request.method == "POST":
            encounter_open = False
            units = Campaign.objects.get(
                name=request.session['campaign']).units
            form = PatientEncounterForm(
                request.POST, unit=units, prefix="form")
            vitals_form = VitalsForm(
                request.POST, unit=units, prefix="vitals_form")
            if form.is_valid() and vitals_form.is_valid():
                encounter = form.save(commit=False)
                vitals = vitals_form.save(commit=False)
                encounter.patient = p
                encounter.active = True
                encounter.campaign = Campaign.objects.get(name=request.session['campaign'])
                encounter.save()
                vitals.encounter = encounter
                vitals.save()
                form.save_m2m()
                if os.environ.get('QLDB_ENABLED') == "TRUE":
                    from .serializers import PatientEncounterSerializer
                    encounter_data = PatientEncounterSerializer(encounter).data
                    create_new_patient_encounter(encounter_data)
                DatabaseChangeLog.objects.create(action="Create", model="PatientEncounter", instance=str(encounter),
                                                 ip=get_client_ip(request), username=request.user.username,
                                                 campaign=Campaign.objects.get(name=request.session['campaign']))
                DatabaseChangeLog.objects.create(action="Create", model="Vitals", instance=str(encounter),
                                                 ip=get_client_ip(request), username=request.user.username,
                                                 campaign=Campaign.objects.get(name=request.session['campaign']))
                if 'submit_encounter' in request.POST:
                    return render(request, 'data/encounter_submitted.html')
                elif 'submit_refer' in request.POST:
                    kwargs = {"id": id}
                    return redirect('main:referral_form_view', **kwargs)
                else:
                    return render(request, 'data/encounter_submitted.html')
        else:
            encounter_open = len(PatientEncounter.objects.filter(patient=p).filter(active=True)) > 0
            units = Campaign.objects.get(
                name=request.session['campaign']).units
            form = PatientEncounterForm(unit=units, prefix="form")
            vitals_form = VitalsForm(unit=units, prefix="vitals_form")
            try:
                encounter = PatientEncounter.objects.filter(
                    patient=p).order_by('timestamp')[0]
                if units == 'i':
                    form.initial = {
                        'timestamp': datetime.now().date(),
                        'body_mass_index': encounter.body_mass_index,
                        'smoking': encounter.smoking,
                        'history_of_diabetes': encounter.history_of_diabetes,
                        'history_of_hypertension': encounter.history_of_hypertension,
                        'history_of_high_cholesterol': encounter.history_of_high_cholesterol,
                        'alcohol': encounter.alcohol,
                        'body_height_primary': math.floor(
                            ((encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) // 12),
                        'body_height_secondary': round((
                                                               (
                                                                           encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) % 12,
                                                       2),
                        'body_weight': round(encounter.body_weight * 2.2046,
                                             2) if encounter.body_weight is not None else 0,
                    }
                else:
                    form.initial = {
                        'timestamp': datetime.now().date(),
                        'body_mass_index': encounter.body_mass_index,
                        'smoking': encounter.smoking,
                        'history_of_diabetes': encounter.history_of_diabetes,
                        'history_of_hypertension': encounter.history_of_hypertension,
                        'history_of_high_cholesterol': encounter.history_of_high_cholesterol,
                        'alcohol': encounter.alcohol,
                        'body_height_primary': encounter.body_height_primary,
                        'body_height_secondary': round(encounter.body_height_secondary, 2),
                        'body_weight': round(encounter.body_weight, 2) if encounter.body_weight is not None else 0,
                    }
            except IndexError:
                form.initial = {
                    'timestamp': datetime.now().date(),
                }
        suffix = p.get_suffix_display() if p.suffix is not None else ""
        return render(request, 'forms/encounter.html',
                      {'form': form, 'vitals_form': vitals_form, 'diagnosis_form': diagnosis_form,
                       'treatment_form': treatment_form,
                       'page_name': 'New Encounter for {} {} {}'.format(p.first_name, p.last_name, suffix),
                       'birth_sex': p.sex_assigned_at_birth, 'patient_id': id, 'units': units, 'telehealth': telehealth,
                       'encounter_open': encounter_open,
                       'page_tip': "Complete form with patient vitals as instructed. Any box with an asterisk (*) is required. For max efficiency, use 'tab' to navigate through this page."})
    else:
        return redirect('/not_logged_in')


def referral_form_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        if request.method == "POST":
            patient = Patient.objects.get(pk=id)
            patient.campaign.add(Campaign.objects.get(
                pk=request.POST['campaign']))
            patient.save()
            update_patient_encounter(
                {'patient': patient.id, 'campaign': request.POST['campaign']})
            return redirect('main:patient_list_view')
        if request.method == "GET":
            return render(request, 'forms/referral.html', {
                'patient_id': id,
                'page_name': "Campaign Referral",
                'campaigns': Campaign.objects.filter(
                    instance=Campaign.objects.get(name=request.session['campaign']).instance).filter(active=True)
            })
    else:
        return redirect('/not_logged_in')
