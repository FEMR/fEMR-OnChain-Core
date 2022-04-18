import os

from django.shortcuts import render, redirect, get_object_or_404
from silk.profiling.profiler import silk_profile

from main.serializers import PatientEncounterSerializer
from main.femr_admin_views import get_client_ip
from main.qldb_interface import update_patient_encounter
from main.forms import (
    PhotoForm,
    VitalsForm,
)
from main.models import (
    Campaign,
    Patient,
    PatientEncounter,
    DatabaseChangeLog,
    Photo,
    Vitals,
    Treatment,
)


@silk_profile("upload-photo-view")
def upload_photo_view(request, patient_id=None, encounter_id=None):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            units = Campaign.objects.get(name=request.user.current_campaign).units
            encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
            patient = get_object_or_404(Patient, pk=patient_id)
            vitals = Vitals.objects.filter(encounter=encounter)
            treatments = Treatment.objects.filter(encounter=encounter)
            aux_form = PhotoForm()
            if request.method == "POST":
                aux_form = __upload_photo_view_post(request, encounter)
            vitals_form = VitalsForm(unit=units)
            suffix = patient.get_suffix_display() if patient.suffix is not None else ""
            return_response = render(
                request,
                "forms/photos_tab.html",
                {
                    "aux_form": aux_form,
                    "vitals": vitals,
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
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def __upload_photo_view_post(request, encounter):
    aux_form = PhotoForm(request.POST, request.FILES)
    if aux_form.is_valid():
        photo = aux_form.save()
        photo.save()
        encounter.photos.add(photo)
        encounter.save()
        aux_form = PhotoForm()
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
    return aux_form


@silk_profile("edit-photo-view-post")
def __edit_photo_view_post(request, patient_id, encounter_id, photo_id):
    units = Campaign.objects.get(name=request.user.current_campaign).units
    encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
    patient = get_object_or_404(Patient, pk=patient_id)
    photo = Photo.objects.get(pk=photo_id)
    aux_form = PhotoForm(request.POST, request.FILES, instance=photo)
    if aux_form.is_valid():
        photo = aux_form.save()
        try:
            photo.save()
        except ValueError:
            photo.delete()
        DatabaseChangeLog.objects.create(
            action="Edit",
            model="Photo",
            instance=str(photo),
            ip=get_client_ip(request),
            username=request.user.username,
            campaign=Campaign.objects.get(name=request.user.current_campaign),
        )
        if os.environ.get("QLDB_ENABLED") == "TRUE":
            encounter_data = PatientEncounterSerializer(encounter).data
            update_patient_encounter(encounter_data)
        vitals_form = VitalsForm(unit=units)
        suffix = patient.get_suffix_display() if patient.suffix is not None else ""
    return render(
        request,
        "forms/photos_tab.html",
        {
            "aux_form": aux_form,
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


@silk_profile("edit-profile-view")
def edit_photo_view(request, patient_id=None, encounter_id=None, photo_id=None):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        if request.method == "POST":
            return_response = __edit_photo_view_post(
                request, patient_id, encounter_id, photo_id
            )
        else:
            photo = Photo.objects.get(pk=photo_id)
            aux_form = PhotoForm(instance=photo)
            return_response = render(
                request,
                "forms/edit_photo.html",
                {
                    "page_name": "Edit Photo",
                    "aux_form": aux_form,
                    "encounter_id": encounter_id,
                    "patient_id": patient_id,
                    "photo_id": photo_id,
                },
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response
