"""
View functions handling displaying data models as sortable, filterable lists.
All views, except auth views and the index view, should be considered to check
for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
import math
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from silk.profiling.profiler import silk_profile

from clinic_messages.models import Message
from main.decorators import is_authenticated
from main.femr_admin_views import get_client_ip
from main.forms import PhotoForm, VitalsForm
from .models import (
    Campaign,
    ChiefComplaint,
    DatabaseChangeLog,
    Patient,
    PatientEncounter,
    Photo,
    Treatment,
    Vitals,
)


@is_authenticated
def patient_delete_view(request, patient_id=None):
    """
    Delete function.

    :param request: Django Request object.
    :param id: The ID of the patient to delete.
    :return: HTTPResponse.
    """
    if request.method == "POST":
        try:
            target_object = get_object_or_404(Patient, pk=patient_id)
            this_campaign = Campaign.objects.get(name=request.user.current_campaign)
            contact = this_campaign.instance.main_contact
            DatabaseChangeLog.objects.create(
                action="Delete",
                model="Patient",
                instance=str(target_object),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=this_campaign,
            )
            message_content = (
                f"{request.user} has deleted a patient record for the fEMR On-Chain "
                f"deployment to {this_campaign} from fEMR On-Chain on {timezone.now()}. "
                "To view audit logs, visit the Admin tab in fEMR On-Chain."
            )
            Message.objects.create(
                sender=request.user,
                recipient=contact,
                subject="WARNING! PATIENT DELETED",
                content=message_content,
            )
            send_mail(
                "WARNING! PATIENT DELETED",
                f"{message_content}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. "
                "PLEASE DO NOT REPLY TO THIS EMAIL. "
                "PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.",
                os.environ.get("DEFAULT_FROM_EMAIL"),
                [contact.email],
            )
            target_object.delete()
        except ObjectDoesNotExist:
            pass
        return_response = render(request, "data/patient_deleted_success.html")
    else:
        target_object = get_object_or_404(Patient, pk=patient_id)
        return_response = render(
            request, "data/delete.html", {"patient": target_object}
        )
    return return_response


@is_authenticated
def delete_chief_complaint(
    _, chief_complaint_id=None, patient_id=None, encounter_id=None
):
    target_object = get_object_or_404(ChiefComplaint, pk=chief_complaint_id)
    target_object.active = False
    target_object.save()
    if encounter_id is not None:
        return_response = redirect(
            "main:chief_complaint_list_view", patient_id, encounter_id
        )
    else:
        return_response = redirect("main:chief_complaint_list_view", patient_id)
    return return_response


@is_authenticated
def delete_treatment_view(request, treatment_id=None):
    target_object = get_object_or_404(Treatment, pk=treatment_id)
    for item in target_object.medication.all():
        item.amount += target_object.amount
        if item.count > 0:
            item.quantity = math.ceil(item.amount / item.count)
        else:
            item.quantity = item.amount
        item.save()
    target_object.delete()
    return redirect(request.META.get("HTTP_REFERER", "/"))


@is_authenticated
@silk_profile("delete-photo-view")
def delete_photo_view(request, patient_id=None, encounter_id=None, photo_id=None):
    """
    Used to edit Encounter objects.

    :param request: Django Request object.
    :param patient_id:
    :param encounter_id: The ID of the object to edit.
    :param photo_id:
    :return: HTTPResponse.
    """
    if request.user.current_campaign == "RECOVERY MODE":
        return_response = redirect("main:home")
    else:
        units = Campaign.objects.get(name=request.user.current_campaign).units
        encounter = get_object_or_404(PatientEncounter, pk=encounter_id)
        patient = get_object_or_404(Patient, pk=patient_id)
        photo = Photo.objects.get(pk=photo_id)
        photo.delete()
        suffix = patient.get_suffix_display() if patient.suffix is not None else ""
        return_response = render(
            request,
            "forms/photos_tab.html",
            {
                "aux_form": PhotoForm(),
                "vitals": Vitals.objects.filter(encounter=encounter),
                "treatments": Treatment.objects.filter(encounter=encounter),
                "vitals_form": VitalsForm(unit=units),
                "page_name": f"Edit Encounter for {patient.first_name}, {patient.last_name}, {suffix}",
                "encounter": encounter,
                "birth_sex": patient.sex_assigned_at_birth,
                "encounter_id": encounter_id,
                "patient_name": f"{patient.first_name} {patient.last_name} {suffix}",
                "units": units,
                "patient": patient,
            },
        )
    return return_response
