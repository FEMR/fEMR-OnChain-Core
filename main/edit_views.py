"""
Handles template rendering and logic for editing web forms.
All views, except auth views and the index view, should be considered
to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
import math
import os

from django.shortcuts import render, redirect, get_object_or_404
from silk.profiling.profiler import silk_profile

from main.serializers import PatientEncounterSerializer
from main.femr_admin_views import get_client_ip
from main.qldb_interface import update_patient, update_patient_encounter
from main.forms import (
    AuxiliaryPatientEncounterForm,
    HistoryOfPresentIllnessForm,
    HistoryPatientEncounterForm,
    PatientDiagnosisForm,
    PatientForm,
    PatientEncounterForm,
    TreatmentForm,
    VitalsForm,
)
from main.models import (
    Campaign,
    Diagnosis,
    HistoryOfPresentIllness,
    Patient,
    PatientDiagnosis,
    PatientEncounter,
    DatabaseChangeLog,
    Vitals,
    Treatment,
)
from main.unit_converters import (
    aux_form_imperial,
    encounter_update_form_initial_imperial,
    history_view_imperial,
    new_diagnosis_imperial,
    new_treatment_imperial,
    new_vitals_imperial,
)


@silk_profile("patient-edit-form-get")
def __patient_edit_form_get(request, patient_id, patient, encounters):
    DatabaseChangeLog.objects.create(
        action="View",
        model="Patient",
        instance=str(patient),
        ip=get_client_ip(request),
        username=request.user.username,
        campaign=Campaign.objects.get(name=request.user.current_campaign),
    )
    form = PatientForm(instance=patient)
    return render(
        request,
        "forms/patient.html",
        {
            "error": "",
            "patient_id": patient_id,
            "encounters": encounters,
            "form": form,
            "page_name": "Returning Patient",
        },
    )


@silk_profile("patient-edit-form-post")
def __patient_edit_form_post(request, patient_id, patient, encounters):
    form = PatientForm(request.POST or None, instance=patient)
    campaign_key = patient.campaign_key
    if form.is_valid():
        patient = form.save()
        patient.campaign_key = campaign_key
        patient.campaign.add(Campaign.objects.get(name=request.user.current_campaign))
        patient.save()
        DatabaseChangeLog.objects.create(
            action="Edit",
            model="Patient",
            instance=str(patient),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.user.current_campaign),
        )
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            update_patient(form.cleaned_data)
        return_response = render(
            request,
            "data/patient_submitted.html",
            {"patient": patient, "encounters": encounters},
        )
    else:
        return_response = render(
            request,
            "forms/patient.html",
            {
                "error": "Form is invalid.",
                "patient_id": patient_id,
                "encounters": encounters,
                "form": form,
                "page_name": "Returning Patient",
            },
        )
    return return_response


@silk_profile("patient-edit-form-view")
def patient_edit_form_view(request, patient_id=None):
    """
    Used to edit Patient objects.

    :param request: Django Request object.
    :param id: The ID of the object to edit.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return redirect("main:home")
        patient = get_object_or_404(Patient, pk=patient_id)
        encounters = PatientEncounter.objects.filter(patient=patient)
        if request.method == "POST":
            return_response = __patient_edit_form_post(
                request, patient_id, patient, encounters
            )
        else:
            return_response = __patient_edit_form_get(
                request, patient_id, patient, encounters
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


@silk_profile("encounter-edit-form-get")
def __encounter_edit_form_get(request, patient_id, encounter_id):
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    patient = get_object_or_404(Patient, pk=patient_id)
    units = Campaign.objects.get(name=request.user.current_campaign).units
    vitals_form = VitalsForm(unit=units)
    DatabaseChangeLog.objects.create(
        action="View",
        model="Patient",
        instance=str(encounter),
        ip=get_client_ip(request),
        username=request.user.username,
        campaign=Campaign.objects.get(name=request.user.current_campaign),
    )
    form = PatientEncounterForm(instance=encounter, unit=units)
    if not encounter.active:
        for field in form:
            try:
                field.widget.attrs["readonly"] = True
            except KeyError:
                pass
            except AttributeError:
                pass
        for field in vitals_form:
            try:
                field.widget.attrs["readonly"] = True
            except KeyError:
                pass
            except AttributeError:
                pass
    if units == "i":
        encounter_update_form_initial_imperial(form, encounter)
    form.initial["timestamp"] = encounter.timestamp
    encounter_active = encounter.active
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/edit_encounter.html",
        {
            "active": encounter_active,
            "aux_form": AuxiliaryPatientEncounterForm(),
            "form": form,
            "vitals": Vitals.objects.filter(encounter=encounter),
            "treatments": Treatment.objects.filter(encounter=encounter),
            "vitals_form": vitals_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
            "units": units,
            "patient": patient,
        },
    )


@silk_profile("encounter-edit-form-post")
def __encounter_edit_form_post(request, patient_id, encounter_id):
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    patient = get_object_or_404(Patient, pk=patient_id)
    units = Campaign.objects.get(name=request.user.current_campaign).units
    photos = encounter.photos.all().iterator()
    treatments = Treatment.objects.filter(encounter=encounter)
    form = PatientEncounterForm(request.POST or None, instance=encounter, unit=units)
    if form.is_valid():
        encounter = form.save(commit=False)
        form.save_m2m()
        encounter.patient = patient
        encounter.active = True
        encounter.photos.set(photos)
        encounter.save()
        DatabaseChangeLog.objects.create(
            action="Edit",
            model="PatientEncounter",
            instance=str(encounter),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.user.current_campaign),
        )
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            encounter_data = PatientEncounterSerializer(encounter).data
            update_patient_encounter(encounter_data)
        if "submit_encounter" in request.POST:
            return_response = render(
                request,
                "data/encounter_submitted.html",
                {"patient_id": patient_id, "encounter_id": encounter_id},
            )
        elif "submit_refer" in request.POST:
            kwargs = {"patient_id": patient_id}
            return_response = redirect("main:referral_form_view", **kwargs)
        else:
            return_response = render(
                request,
                "data/encounter_submitted.html",
                {"patient_id": patient_id, "encounter_id": encounter_id},
            )
    else:
        form.initial["timestamp"] = encounter.timestamp
        encounter_active = encounter.active
        suffix = patient.get_suffix_display() if patient.suffix is not None else ""
        return_response = render(
            request,
            "forms/edit_encounter.html",
            {
                "active": encounter_active,
                "aux_form": AuxiliaryPatientEncounterForm(),
                "form": form,
                "vitals": Vitals.objects.filter(encounter=encounter),
                "treatments": treatments,
                "vitals_form": VitalsForm(unit=units),
                "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
                "encounter": encounter,
                "birth_sex": patient.sex_assigned_at_birth,
                "encounter_id": encounter_id,
                "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
                "units": units,
                "patient": patient,
            },
        )
    return return_response


@silk_profile("encounter-edit-form-view")
def encounter_edit_form_view(request, patient_id=None, encounter_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param patient_id: The ID of the object to edit.
    :param encounter_id:
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
            return_response = __encounter_edit_form_post(
                request, patient_id, encounter_id
            )
        else:
            return_response = __encounter_edit_form_get(
                request, patient_id, encounter_id
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


@silk_profile("new-diagnosis-view")
def new_diagnosis_view(request, patient_id=None, encounter_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param patient_id: The ID of the object to edit.
    :param encounter_id:
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            return_response = __new_diagnosis_view_body(
                request, patient_id, encounter_id
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def __new_diagnosis_view_body(request, patient_id, encounter_id):
    campaign = Campaign.objects.get(name=request.user.current_campaign)
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    patient = get_object_or_404(Patient, pk=patient_id)
    treatment_form = TreatmentForm()
    treatment_form.fields["medication"].queryset = campaign.inventory.entries.all()
    querysets = PatientDiagnosis.objects.filter(encounter=encounter)
    diagnosis_set = PatientDiagnosis.objects.filter(encounter=encounter)
    if len(diagnosis_set) > 0:
        diagnosis_form = PatientDiagnosisForm(instance=diagnosis_set[0])
    else:
        diagnosis_form = PatientDiagnosisForm()
    if request.method == "POST":
        diagnosis_form = new_diagnosis_view_post(request, encounter, diagnosis_set)
    form = PatientEncounterForm(instance=encounter, unit=campaign.units)
    if campaign.units == "i":
        new_diagnosis_imperial(form, encounter)
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    if len(querysets) > 0:
        item = querysets[0].diagnosis.all()
        for query_item in querysets:
            item.union(query_item.diagnosis.all())
        treatment_form.fields["diagnosis"].queryset = item
        treatment_active = True
    else:
        treatment_form.fields["diagnosis"].queryset = Diagnosis.objects.none()
        treatment_active = False
    return render(
        request,
        "forms/treatment_tab.html",
        {
            "active": encounter.active,
            "aux_form": AuxiliaryPatientEncounterForm(instance=encounter),
            "form": form,
            "vitals": Vitals.objects.filter(encounter=encounter),
            "treatments": Treatment.objects.filter(encounter=encounter),
            "vitals_form": VitalsForm(unit=campaign.units),
            "diagnosis_form": diagnosis_form,
            "treatment_form": treatment_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
            "units": campaign.units,
            "patient": patient,
            "treatment_active": treatment_active,
        },
    )


def new_diagnosis_view_post(request, encounter, diagnosis_set):
    if len(diagnosis_set) > 0:
        diagnosis_form = PatientDiagnosisForm(request.POST, instance=diagnosis_set[0])
    else:
        diagnosis_form = PatientDiagnosisForm(request.POST)
    if diagnosis_form.is_valid():
        if len(diagnosis_set) > 1:
            PatientDiagnosis.objects.exclude(pk=diagnosis_set[0].id).delete()
        diagnosis = diagnosis_form.save(commit=False)
        diagnosis.encounter = encounter
        diagnosis.save()
        diagnosis_form.save_m2m()
        DatabaseChangeLog.objects.create(
            action="Edit",
            model="PatientEncounter",
            instance=str(encounter),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.user.current_campaign),
        )
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            encounter_data = PatientEncounterSerializer(encounter).data
            update_patient_encounter(encounter_data)
    return diagnosis_form


@silk_profile("new-treatment-view")
def new_treatment_view(request, patient_id=None, encounter_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param patient_id: The ID of the object to edit.
    :param encounter_id:
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            return_response = __new_treatment_view_body(
                request, patient_id, encounter_id
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def __new_treatment_view_body(request, patient_id, encounter_id):
    campaign = Campaign.objects.get(name=request.user.current_campaign)
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    patient = get_object_or_404(Patient, pk=patient_id)
    treatment_form = TreatmentForm()
    treatment_form.fields[
        "medication"
    ].queryset = campaign.inventory.entries.all().iterator()
    querysets = list(PatientDiagnosis.objects.filter(encounter=encounter))
    if len(querysets) > 0:
        item = querysets.pop().diagnosis.all()
        for query_item in querysets:
            item.union(query_item.diagnosis.all())
        treatment_form.fields["diagnosis"].queryset = item
        treatment_active = True
    else:
        treatment_form.fields["diagnosis"].queryset = Diagnosis.objects.none()
        treatment_active = False
    diagnosis_set = list(PatientDiagnosis.objects.filter(encounter=encounter))
    if len(diagnosis_set) > 0:
        diagnosis_form = PatientDiagnosisForm(instance=diagnosis_set[0])
    else:
        diagnosis_form = PatientDiagnosisForm()
    if request.method == "POST":
        treatment_form = __treatment_view_post(request, encounter)
    form = PatientEncounterForm(instance=encounter, unit=campaign.units)
    if campaign.units == "i":
        new_treatment_imperial(form, encounter)
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/treatment_tab.html",
        {
            "form": form,
            "aux_form": AuxiliaryPatientEncounterForm(instance=encounter),
            "vitals": Vitals.objects.filter(encounter=encounter),
            "treatments": Treatment.objects.filter(encounter=encounter),
            "vitals_form": VitalsForm(unit=campaign.units),
            "diagnosis_form": diagnosis_form,
            "treatment_form": treatment_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
            "units": campaign.units,
            "patient": patient,
            "treatment_active": treatment_active,
        },
    )


def __treatment_view_post(request, encounter):
    treatment_form = TreatmentForm(request.POST)
    if treatment_form.is_valid():
        treatment = treatment_form.save(commit=False)
        treatment.encounter = encounter
        treatment.prescriber = request.user
        if treatment.administration_schedule is not None:
            treatment.amount = (
                treatment.days * treatment.administration_schedule.modifier
            )
        else:
            treatment.amount = 1
        treatment.save()
        treatment_form.save_m2m()
        for item in treatment.medication.all().iterator():
            item.amount -= treatment.amount
            if item.count > 0:
                item.quantity = math.ceil(item.amount / item.count)
            else:
                item.quantity = item.amount
            item.save()
        treatment_form = TreatmentForm()
        DatabaseChangeLog.objects.create(
            action="Edit",
            model="PatientEncounter",
            instance=str(encounter),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.user.current_campaign),
        )
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            encounter_data = PatientEncounterSerializer(encounter).data
            update_patient_encounter(encounter_data)
    return treatment_form


@silk_profile("aux-form-view")
def aux_form_view(request, patient_id=None, encounter_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param patient_id: The ID of the object to edit.
    :param encounter_id:
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
            patient = get_object_or_404(Patient, pk=patient_id)
            treatment_form = TreatmentForm()
            querysets = list(PatientDiagnosis.objects.filter(encounter=encounter))
            if len(querysets) > 0:
                item = querysets.pop().diagnosis.all()
                for query_item in querysets:
                    item.union(query_item.diagnosis.all())
                treatment_form.fields["diagnosis"].queryset = item
            else:
                treatment_form.fields["diagnosis"].queryset = Diagnosis.objects.none()
            diagnosis_set = PatientDiagnosis.objects.filter(encounter=encounter)
            if len(diagnosis_set) > 0:
                diagnosis_form = PatientDiagnosisForm(instance=diagnosis_set[0])
            else:
                diagnosis_form = PatientDiagnosisForm()
            if request.method == "POST":
                return_response = __aux_form_view_post(
                    request, encounter_id, patient, treatment_form, diagnosis_form
                )
            else:
                return_response = __aux_form_view_get(
                    request,
                    encounter_id,
                    patient,
                    treatment_form,
                    diagnosis_form,
                )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def __aux_form_view_post(
    request, encounter_id, patient, treatment_form, diagnosis_form
):
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    aux_form = AuxiliaryPatientEncounterForm(request.POST)
    if aux_form.is_valid():
        return_response = __aux_form_is_valid(request, encounter, treatment_form)
    else:
        return_response = __aux_form_invalid(
            request,
            encounter_id,
            patient,
            treatment_form,
            diagnosis_form,
        )
    return return_response


def __aux_form_view_get(request, encounter_id, patient, treatment_form, diagnosis_form):
    encounter = PatientEncounter.objects.get(pk=encounter_id)
    units = Campaign.objects.get(name=request.user.current_campaign).units
    form = PatientEncounterForm(instance=encounter, unit=units)
    if units == "i":
        aux_form_imperial(form, encounter)
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/treatment_tab.html",
        {
            "form": form,
            "aux_form": AuxiliaryPatientEncounterForm(instance=encounter),
            "vitals": Vitals.objects.filter(encounter=encounter),
            "treatments": Treatment.objects.filter(encounter=encounter),
            "vitals_form": VitalsForm(unit=units),
            "diagnosis_form": diagnosis_form,
            "treatment_form": treatment_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
            "units": units,
            "patient": patient,
        },
    )


def __aux_form_invalid(request, encounter_id, patient, treatment_form, diagnosis_form):
    units = Campaign.objects.get(name=request.user.current_campaign).units
    encounter = PatientEncounter.objects.get(pk=encounter_id)
    form = PatientEncounterForm(instance=encounter, unit=units)
    if units == "i":
        aux_form_imperial(form, encounter)
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/treatment_tab.html",
        {
            "form": form,
            "aux_form": AuxiliaryPatientEncounterForm(instance=encounter),
            "vitals": Vitals.objects.filter(encounter=encounter),
            "treatments": Treatment.objects.filter(encounter=encounter),
            "vitals_form": VitalsForm(unit=units),
            "diagnosis_form": diagnosis_form,
            "treatment_form": treatment_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
            "units": units,
            "patient": patient,
        },
    )


def __aux_form_is_valid(request, encounter, treatment_form):
    encounter.procedure = request.POST["procedure"]
    encounter.pharmacy_notes = request.POST["pharmacy_notes"]
    encounter.save()
    querysets = list(PatientDiagnosis.objects.filter(encounter=encounter))
    if len(querysets) > 0:
        item = querysets.pop().diagnosis.all()
        for query_item in querysets:
            item.union(query_item.diagnosis.all())
        treatment_form.fields["diagnosis"].queryset = item
    else:
        treatment_form.fields["diagnosis"].queryset = Diagnosis.objects.none()
    DatabaseChangeLog.objects.create(
        action="Edit",
        model="PatientEncounter",
        instance=str(encounter),
        ip=get_client_ip(request),
        username=request.user.username,
        campaign=Campaign.objects.get(name=request.user.current_campaign),
    )
    if os.environ.get("QLDB_ENABLED") == "TRUE":
        encounter_data = PatientEncounterSerializer(encounter).data
        update_patient_encounter(encounter_data)
    return render(
        request,
        "data/encounter_submitted.html",
        {"patient_id": encounter.patient.id, "encounter_id": encounter.id},
    )


@silk_profile("history-view")
def history_view(request, patient_id=None, encounter_id=None):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            units = Campaign.objects.get(name=request.user.current_campaign).units
            encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
            patient = get_object_or_404(Patient, pk=patient_id)
            aux_form = HistoryPatientEncounterForm(instance=encounter)
            if request.method == "POST":
                aux_form = HistoryPatientEncounterForm(request.POST)
                if aux_form.is_valid():
                    encounter.medical_history = request.POST["medical_history"]
                    encounter.social_history = request.POST["social_history"]
                    encounter.current_medications = request.POST["current_medications"]
                    encounter.family_history = request.POST["family_history"]
                    encounter.save()
                    DatabaseChangeLog.objects.create(
                        action="Edit",
                        model="PatientEncounter",
                        instance=str(encounter),
                        ip=get_client_ip(request),
                        username=request.user.username,
                        campaign=Campaign.objects.get(
                            name=request.user.current_campaign
                        ),
                    )
                    if os.environ.get("QLDB_ENABLED") == "TRUE":
                        encounter_data = PatientEncounterSerializer(encounter).data
                        update_patient_encounter(encounter_data)
                    return_response = render(
                        request,
                        "data/encounter_submitted.html",
                        {"patient_id": patient_id, "encounter_id": encounter_id},
                    )
                else:
                    form = PatientEncounterForm(instance=encounter, unit=units)
                    vitals_form = VitalsForm(unit=units)
                    if units == "i":
                        history_view_imperial(form, encounter)
                    suffix = (
                        patient.get_suffix_display()
                        if patient.suffix is not None
                        else ""
                    )
                    return_response = render(
                        request,
                        "forms/history_tab.html",
                        {
                            "form": form,
                            "aux_form": aux_form,
                            "vitals": Vitals.objects.filter(encounter=encounter),
                            "treatments": Treatment.objects.filter(encounter=encounter),
                            "vitals_form": vitals_form,
                            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
                            "encounter": encounter,
                            "birth_sex": patient.sex_assigned_at_birth,
                            "patient_id": patient_id,
                            "encounter_id": encounter_id,
                            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
                            "units": units,
                            "patient": patient,
                        },
                    )
            else:
                return_response = __history_view_get(
                    request, encounter_id, units, patient, aux_form
                )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def __history_view_get(request, encounter_id, units, patient, aux_form):
    encounter = PatientEncounter.objects.get(pk=encounter_id)
    treatments = Treatment.objects.filter(encounter=encounter)
    form = PatientEncounterForm(instance=encounter, unit=units)
    vitals_form = VitalsForm(unit=units)
    if units == "i":
        history_view_imperial(form, encounter)
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/history_tab.html",
        {
            "form": form,
            "aux_form": aux_form,
            "vitals": Vitals.objects.filter(encounter=encounter),
            "treatments": treatments,
            "vitals_form": vitals_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
            "units": units,
            "patient": patient,
        },
    )


@silk_profile("new-vitals-view")
def new_vitals_view(request, patient_id=None, encounter_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param patient_id: The ID of the object to edit.
    :param encounter_id: THe ID of the encounter the vitals object is connected to.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            units = Campaign.objects.get(name=request.user.current_campaign).units
            encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
            patient = get_object_or_404(Patient, pk=patient_id)
            vitals = Vitals.objects.filter(encounter=encounter)
            treatments = Treatment.objects.filter(encounter=encounter)
            if request.method == "POST":
                new_vitals_view_post(request, units, encounter)
            form = PatientEncounterForm(instance=encounter, unit=units)
            vitals_form = VitalsForm(unit=units)
            if units == "i":
                new_vitals_imperial(form, encounter)
            suffix = patient.get_suffix_display() if patient.suffix is not None else ""
            return_response = render(
                request,
                "forms/edit_encounter.html",
                {
                    "active": encounter.active,
                    "form": form,
                    "vitals": vitals,
                    "treatments": treatments,
                    "vitals_form": vitals_form,
                    "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
                    "encounter": encounter,
                    "birth_sex": patient.sex_assigned_at_birth,
                    "encounter_id": encounter_id,
                    "patient": patient,
                    "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
                    "units": units,
                },
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def new_vitals_view_post(request, units, encounter):
    vitals_form = VitalsForm(request.POST, unit=units)
    if vitals_form.is_valid():
        vitals = vitals_form.save(commit=False)
        vitals.encounter = encounter
        vitals.save()
        DatabaseChangeLog.objects.create(
            action="New",
            model="Vitals",
            instance=str(encounter),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.user.current_campaign),
        )
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            encounter_data = PatientEncounterSerializer(encounter).data
            update_patient_encounter(encounter_data)


@silk_profile("hpi-view-post")
def __hpi_view_post(request, patient_id, encounter_id):
    units = Campaign.objects.get(name=request.user.current_campaign).units
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    patient = get_object_or_404(Patient, pk=patient_id)
    vitals = Vitals.objects.filter(encounter=encounter)
    treatments = Treatment.objects.filter(encounter=encounter)
    hpis = []
    for query_item in encounter.chief_complaint.all().iterator():
        hpi_object = HistoryOfPresentIllness.objects.get_or_create(
            encounter=encounter, chief_complaint=query_item
        )[0]
        hpis.append(
            {
                "id": hpi_object.id,
                "form": HistoryOfPresentIllnessForm(instance=hpi_object),
                "complaint": query_item,
            }
        )
    vitals_form = VitalsForm(unit=units)
    suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/hpi_tab.html",
        {
            "hpis": hpis,
            "vitals": vitals,
            "treatments": treatments,
            "vitals_form": vitals_form,
            "page_name": f"Edit Encounter for {patient.first_name} {patient.last_name} {suffix}",
            "encounter": encounter,
            "birth_sex": patient.sex_assigned_at_birth,
            "encounter_id": encounter_id,
            "patient_name": f"{patient.first_name}, {patient.last_name}, {suffix}",
            "units": units,
            "patient": patient,
        },
    )


@silk_profile("hpi-view")
def hpi_view(request, patient_id=None, encounter_id=None):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            return_response = __hpi_view_post(request, patient_id, encounter_id)
    else:
        return_response = redirect("/not_logged_in")
    return return_response


@silk_profile("submit-hpi-view")
def submit_hpi_view(request, patient_id=None, encounter_id=None, hpi_id=None):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
            encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
            history = HistoryOfPresentIllness.objects.get(pk=hpi_id)
            aux_form = HistoryOfPresentIllnessForm(request.POST, instance=history)
            if aux_form.is_valid():
                updated_history = aux_form.save()
                updated_history.save()
                DatabaseChangeLog.objects.create(
                    action="Edit",
                    model="PatientEncounter",
                    instance=str(encounter),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=Campaign.objects.get(name=request.user.current_campaign),
                )
                if os.environ.get("QLDB_ENABLED") == "TRUE":
                    encounter_data = PatientEncounterSerializer(encounter).data
                    update_patient_encounter(encounter_data)
            return_response = redirect(
                "main:hpi_view", patient_id=patient_id, encounter_id=encounter_id
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def patient_medical(request, patient_id=None):
    if request.user.is_authenticated:
        encounters = PatientEncounter.objects.filter(patient__pk=patient_id).order_by(
            "-timestamp"
        )
        if encounters:
            encounter = encounters[0]
            return_response = redirect(
                "main:encounter_edit_form_view",
                patient_id=patient_id,
                encounter_id=encounter.pk,
            )
        else:
            return_response = redirect(
                "main:patient_encounter_form_view", patient_id=patient_id
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response
