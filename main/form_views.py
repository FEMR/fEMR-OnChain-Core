"""
Handles template rendering and logic for web forms.

All views, except auth views and the index view, should be considered to
check for a valid and authenticated user.

If one is not found, they will direct to the appropriate error page.
"""
import math
import os
from datetime import datetime

from django.shortcuts import render, redirect

from main.femr_admin_views import get_client_ip

from main.forms import (
    DiagnosisForm,
    PatientForm,
    PatientEncounterForm,
    TreatmentForm,
    VitalsForm,
)
from main.models import Campaign, Patient, DatabaseChangeLog, PatientEncounter, cal_key
from main.serializers import PatientEncounterSerializer
from main.qldb_interface import (
    create_new_patient,
    create_new_patient_encounter,
    update_patient_encounter,
)


def __patient_form_view_get(request, campaign):
    form = PatientForm()
    form.fields["race"].queryset = campaign.race_options
    form.fields["ethnicity"].queryset = campaign.ethnicity_options
    return render(
        request,
        "forms/new_patient.html",
        {
            "ssn_error": False,
            "phone_error": False,
            "email_error": False,
            "shared_phone_error": False,
            "shared_email_error": False,
            "match_list": None,
            "form": form,
            "page_name": "New Patient",
            "page_tip": "Complete form with patient demographics as instructed."
            "Any box with an asterisk (*) is required. "
            "Shared contact information would be if two patients have a "
            "household phone or email that they share, for example.",
        },
    )


def __patient_form_view_post(request, campaign):
    form = PatientForm(request.POST)
    ssn_error = False
    phone_error = False
    email_error = False
    shared_phone_error = False
    shared_email_error = False
    match = None
    if form.is_valid():
        item = form.save()
        item.campaign.add(campaign)
        key = None
        while key is None:
            key = cal_key(campaign)
        item.campaign_key = key
        item.save()
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            create_new_patient(form.cleaned_data)
        DatabaseChangeLog.objects.create(
            action="Create",
            model="Patient",
            instance=str(item),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.session["campaign"]),
        )
        if item.id != "" and item.id is not None:
            return_response = render(
                request,
                "data/patient_submitted.html",
                {"patient": item, "encounters": []},
            )
        else:
            return_response = render(request, "data/patient_not_submitted.html")
    else:
        if (
            "social_security_number" in form.errors
            and "Must be 4 or 9 digits" not in form.errors["social_security_number"][0]
        ):
            ssn_error = True
            match = Patient.objects.get(
                social_security_number=form.data["social_security_number"]
            )
        if "phone_number" in form.errors:
            phone_error = True
            match = Patient.objects.filter(phone_number=form.data["phone_number"])
        if "email_address" in form.errors:
            email_error = True
            match = Patient.objects.filter(email_address=form.data["email_address"])
        form.fields["race"].queryset = campaign.race_options
        form.fields["ethnicity"].queryset = campaign.ethnicity_options
        return_response = render(
            request,
            "forms/new_patient.html",
            {
                "ssn_error": ssn_error,
                "phone_error": phone_error,
                "email_error": email_error,
                "shared_phone_error": shared_phone_error,
                "shared_email_error": shared_email_error,
                "match_list": match,
                "form": form,
                "page_name": "New Patient",
                "page_tip": "Complete form with patient demographics as instructed. "
                "Any box with an asterisk (*) is required. "
                "Shared contact information would be if two patients have a "
                "household phone or email that they share, for example.",
            },
        )
    return return_response


def patient_form_view(request):
    """
    Used to create new Patient objects.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.session["campaign"] == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            campaign = Campaign.objects.get(name=request.session["campaign"])
            if request.method == "POST":
                return_response = __patient_form_view_post(request, campaign)
            else:
                return_response = __patient_form_view_get(request, campaign)
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def __patient_encounter_form_get(request, patient):
    telehealth = Campaign.objects.get(name=request.session["campaign"]).telehealth
    treatment_form = TreatmentForm()
    diagnosis_form = DiagnosisForm()
    encounter_open = (
        len(PatientEncounter.objects.filter(patient=patient).filter(active=True)) > 0
    )
    units = Campaign.objects.get(name=request.session["campaign"]).units
    form = PatientEncounterForm(unit=units, prefix="form")
    vitals_form = VitalsForm(unit=units, prefix="vitals_form")
    try:
        encounter = PatientEncounter.objects.filter(patient=patient).order_by(
            "timestamp"
        )[0]
        if units == "i":
            form.initial = {
                "timestamp": datetime.now().date(),
                "body_mass_index": encounter.body_mass_index,
                "smoking": encounter.smoking,
                "history_of_diabetes": encounter.history_of_diabetes,
                "history_of_hypertension": encounter.history_of_hypertension,
                "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
                "alcohol": encounter.alcohol,
                "body_height_primary": math.floor(
                    (
                        (
                            encounter.body_height_primary * 100
                            + encounter.body_height_secondary
                        )
                        / 2.54
                    )
                    // 12
                ),
                "body_height_secondary": round(
                    (
                        (
                            encounter.body_height_primary * 100
                            + encounter.body_height_secondary
                        )
                        / 2.54
                    )
                    % 12,
                    2,
                ),
                "body_weight": round(encounter.body_weight * 2.2046, 2)
                if encounter.body_weight is not None
                else 0,
            }
        else:
            form.initial = {
                "timestamp": datetime.now().date(),
                "body_mass_index": encounter.body_mass_index,
                "smoking": encounter.smoking,
                "history_of_diabetes": encounter.history_of_diabetes,
                "history_of_hypertension": encounter.history_of_hypertension,
                "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
                "alcohol": encounter.alcohol,
                "body_height_primary": encounter.body_height_primary,
                "body_height_secondary": round(encounter.body_height_secondary, 2),
                "body_weight": round(encounter.body_weight, 2)
                if encounter.body_weight is not None
                else 0,
            }
    except IndexError:
        form.initial = {
            "timestamp": datetime.now().date(),
        }
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/encounter.html",
        {
            "form": form,
            "vitals_form": vitals_form,
            "diagnosis_form": diagnosis_form,
            "treatment_form": treatment_form,
            "page_name": f"New Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "birth_sex": patient.sex_assigned_at_birth,
            "patient_id": patient.id,
            "units": units,
            "telehealth": telehealth,
            "encounter_open": encounter_open,
            "page_tip": "Complete form with patient vitals as instructed. "
            "Any box with an asterisk (*) is required. "
            "For max efficiency, use 'tab' to navigate through this page.",
        },
    )


def __patient_encounter_form_post(request, patient):
    telehealth = Campaign.objects.get(name=request.session["campaign"]).telehealth
    units = Campaign.objects.get(name=request.session["campaign"]).units
    encounter_open = (
        len(PatientEncounter.objects.filter(patient=patient).filter(active=True)) > 0
    )
    form = PatientEncounterForm(request.POST, unit=units, prefix="form")
    vitals_form = VitalsForm(request.POST, unit=units, prefix="vitals_form")
    treatment_form = TreatmentForm()
    diagnosis_form = DiagnosisForm()
    if form.is_valid() and vitals_form.is_valid():
        encounter = form.save(commit=False)
        vitals = vitals_form.save(commit=False)
        encounter.patient = patient
        encounter.active = True
        encounter.campaign = Campaign.objects.get(name=request.session["campaign"])
        encounter.save()
        vitals.encounter = encounter
        vitals.save()
        form.save_m2m()
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            encounter_data = PatientEncounterSerializer(encounter).data
            create_new_patient_encounter(encounter_data)
        DatabaseChangeLog.objects.create(
            action="Create",
            model="PatientEncounter",
            instance=str(encounter),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.session["campaign"]),
        )
        DatabaseChangeLog.objects.create(
            action="Create",
            model="Vitals",
            instance=str(encounter),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.session["campaign"]),
        )
        if "submit_encounter" in request.POST:
            return_response = render(
                request,
                "data/encounter_submitted.html",
                {"patient_id": patient.id, "encounter_id": encounter.id},
            )
        elif "submit_refer" in request.POST:
            kwargs = {"patient_id": patient.id}
            return_response = redirect("main:referral_form_view", **kwargs)
        else:
            return_response = render(
                request,
                "data/encounter_submitted.html",
                {"patient_id": patient.id, "encounter_id": encounter.id},
            )
    else:
        suffix = patient.get_suffix_display() if patient.suffix is not None else ""
        return_response = render(
            request,
            "forms/encounter.html",
            {
                "form": form,
                "vitals_form": vitals_form,
                "diagnosis_form": diagnosis_form,
                "treatment_form": treatment_form,
                "page_name": f"New Encounter for {patient.first_name} {patient.last_name} {suffix}",
                "birth_sex": patient.sex_assigned_at_birth,
                "patient_id": patient.id,
                "units": units,
                "telehealth": telehealth,
                "encounter_open": encounter_open,
                "page_tip": "Complete form with patient vitals as instructed. "
                "Any box with an asterisk (*) is required. "
                "For max efficiency, use 'tab' to navigate through this page.",
            },
        )
    return return_response


def patient_encounter_form_view(request, patient_id=None):
    """
    Used to create new PatientEncounter objects.

    :param request: Django Request object.
    :param patient_id: The internal ID of the patient to be edited.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        patient = Patient.objects.get(pk=patient_id)
        if request.session["campaign"] == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            if request.method == "POST":
                return_response = __patient_encounter_form_post(request, patient)
            else:
                return_response = __patient_encounter_form_get(request, patient)
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def referral_form_view(request, patient_id=None):
    if request.user.is_authenticated:
        if request.session["campaign"] == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
            patient = Patient.objects.get(pk=patient_id)
            patient.campaign.add(Campaign.objects.get(pk=request.POST["campaign"]))
            patient.save()
            if os.environ.get("QLDB_ENABLED") == "TRUE":
                update_patient_encounter(
                    {"patient": patient.id, "campaign": request.POST["campaign"]}
                )
            return_response = redirect("main:patient_list_view")
        elif request.method == "GET":
            return_response = render(
                request,
                "forms/referral.html",
                {
                    "patient_id": patient_id,
                    "page_name": "Campaign Referral",
                    "campaigns": Campaign.objects.filter(
                        instance=Campaign.objects.get(
                            name=request.session["campaign"]
                        ).instance
                    ).filter(active=True),
                },
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response
