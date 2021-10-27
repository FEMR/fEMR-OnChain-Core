"""
View functions handling displaying data models as sortable, filterable lists.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from clinic_messages.models import Message
from main.femr_admin_views import get_client_ip
from .models import Campaign, ChiefComplaint, DatabaseChangeLog, Patient


def patient_delete_view(request, id=None):
    """
    Delete function.

    :param request: Django Request object.
    :param id: The ID of the patient to delete.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                p = get_object_or_404(Patient, pk=id)
                this_campaign = Campaign.objects.get(name=request.session["campaign"])
                contact = this_campaign.instance.main_contact
                DatabaseChangeLog.objects.create(
                    action="Delete",
                    model="Patient",
                    instance=str(p),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=this_campaign,
                )
                message_content = """{0} has deleted a patient record for the fEMR On-Chain deployment to {1} from fEMR On-Chain on {2}.
To view audit logs, visit the Admin tab in fEMR On-Chain.""".format(
                    request.user, this_campaign, timezone.now()
                )
                Message.objects.create(
                    sender=request.user,
                    recipient=contact,
                    subject="WARNING! PATIENT DELETED",
                    content=message_content,
                )
                send_mail(
                    "WARNING! PATIENT DELETED",
                    "{0}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.".format(
                        message_content
                    ),
                    os.environ.get("DEFAULT_FROM_EMAIL"),
                    [contact.email],
                )
                p.delete()
            except ObjectDoesNotExist:
                pass
            return render(request, "data/patient_deleted_success.html")
        else:
            p = get_object_or_404(Patient, pk=id)
            return render(request, "data/delete.html", {"patient": p})
    else:
        return redirect("main:not_logged_in")


def delete_chief_complaint(request, id=None, patient_id=None, encounter_id=None):
    """
    Delete a selected Chief Complaint and redirect back.
    :param request:
    :param id:
    :param patient_id:
    :param encounter_id:
    :return:
    """
    if request.user.is_authenticated:
        p = get_object_or_404(ChiefComplaint, pk=id)
        p.active = False
        p.save()
        if encounter_id is not None:
            return redirect("main:chief_complaint_list_view", patient_id, encounter_id)
        else:
            return redirect("main:chief_complaint_list_view", patient_id)
    else:
        return redirect("main:not_logged_in")
