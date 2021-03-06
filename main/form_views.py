"""
Handles template rendering and logic for web forms.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from main.femr_admin_views import get_client_ip
import math
import os
from django.shortcuts import render, redirect

from .forms import PatientForm, PatientEncounterForm
from .models import Campaign, Patient, DatabaseChangeLog, PatientEncounter
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
        ssn_error = False
        phone_error = False
        email_error = False
        shared_phone_error = False
        shared_email_error = False
        match = None
        if request.method == "GET":
            form = PatientForm()
        if request.method == "POST":
            form = PatientForm(request.POST)
            if form.is_valid():
                t = form.save()
                t.campaign.add(Campaign.objects.get(
                    name=request.session['campaign']))
                t.save()
                if os.environ.get('QLDB_ENABLED') == "TRUE":
                    create_new_patient(form.cleaned_data)
                DatabaseChangeLog.objects.create(action="Create", model="Patient", instance=str(t),
                                                 ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                if t.id != '' and t.id != None:
                    return render(request, "data/patient_submitted.html", {'patient_id': t.id})
                else:
                    return render(request, "data/patient_not_submitted.html")
            else:
                if 'social_security_number' in form.errors and 'Must be 4 or 9 digits' not in form.errors['social_security_number'][0]:
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
        return render(request, 'forms/new_patient.html', {'ssn_error': ssn_error,
                                                          'phone_error': phone_error,
                                                          'email_error': email_error,
                                                          'shared_phone_error': shared_phone_error,
                                                          'shared_email_error': shared_email_error,
                                                          'match_list': match,
                                                          'form': form,
                                                          'page_name': 'New Patient',
                                                          'page_tip': "Complete form with patient demographics as instructed. Any box with an asterix (*) is required. Shared contact information would be if two patients have a household phone or email that they share, for example."})
    else:
        return redirect('/not_logged_in')


def patient_encounter_form_view(request, id=None):
    """
    Used to create new PatientEncounter objects.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        telehealth = Campaign.objects.get(name=request.session['campaign']).telehealth
        p = Patient.objects.get(pk=id)
        if request.method == "POST":
            units = Campaign.objects.get(
                name=request.session['campaign']).units
            form = PatientEncounterForm(request.POST, unit=units)
            if form.is_valid():
                encounter = form.save(commit=False)
                encounter.patient = p
                encounter.save()
                if os.environ.get('QLDB_ENABLED') == "TRUE":
                    create_new_patient_encounter(form.cleaned_data)
                DatabaseChangeLog.objects.create(action="Create", model="PatientEncounter", instance=str(encounter),
                                                 ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                if 'submit_encounter' in request.POST:
                    return render(request, 'data/encounter_submitted.html')
                elif 'submit_refer' in request.POST:
                    kwargs = {"id": id}
                    return redirect('main:referral_form_view', **kwargs)
                else:
                    return render(request, 'data/encounter_submitted.html')
        else:
            units = Campaign.objects.get(
                name=request.session['campaign']).units
            form = PatientEncounterForm(unit=units)
            try:
                encounter = PatientEncounter.objects.filter(
                    patient=p).order_by('timestamp')[0]
                if units == 'i':
                    form.initial = {
                        'body_mass_index': encounter.body_mass_index,
                        'smoking': encounter.smoking,
                        'history_of_diabetes': encounter.history_of_diabetes,
                        'history_of_hypertension': encounter.history_of_hypertension,
                        'history_of_high_cholesterol': encounter.history_of_high_cholesterol,
                        'alcohol': encounter.alcohol,
                        'body_height_primary': math.floor(
                            ((encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) // 12),
                        'body_height_secondary': round((
                            (encounter.body_height_primary * 100 + encounter.body_height_secondary) / 2.54) % 12, 2),
                        'body_weight': round(encounter.body_weight * 2.2046, 2),
                    }
                else:
                    form.initial = {
                        'body_mass_index': encounter.body_mass_index,
                        'smoking': encounter.smoking,
                        'history_of_diabetes': encounter.history_of_diabetes,
                        'history_of_hypertension': encounter.history_of_hypertension,
                        'history_of_high_cholesterol': encounter.history_of_high_cholesterol,
                        'alcohol': encounter.alcohol,
                        'body_height_primary': encounter.body_height_primary,
                        'body_height_secondary': round(encounter.body_height_secondary, 2),
                        'body_weight': round(encounter.body_weight, 2),
                    }
            except IndexError:
                form = PatientEncounterForm(unit=units)
        suffix = p.get_suffix_display() if p.suffix is not None else ""
        return render(request, 'forms/encounter.html',
                      {'form': form, 'page_name': 'New Encounter for {} {} {}'.format(p.first_name, p.last_name, suffix),
                       'birth_sex': p.sex_assigned_at_birth, 'patient_id': id, 'units': units, 'telehealth': telehealth,
                       'page_tip': "Complete form with patient vitals as instructed. Any box with an asterix (*) is required. For max efficiency, use 'tab' to navigate through this page."})
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
                'campaigns': Campaign.objects.filter(instance=(Campaign.objects.get(name=request.session['campaign']).instance)).filter(active=True)
            })
    else:
        return redirect('/not_logged_in')
