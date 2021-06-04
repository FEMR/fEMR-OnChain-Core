"""
View functions handling displaying data models as sortable, filterable lists.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from clinic_messages.models import Message
from django.forms.models import construct_instance
from main.femr_admin_views import get_client_ip
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Campaign, DatabaseChangeLog, Patient


def patient_delete_view(request, id=None):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                p = get_object_or_404(Patient, pk=id)
                this_campaign = Campaign.objects.get(
                    name=request.session['campaign'])
                contact = this_campaign.instance.main_contact
                DatabaseChangeLog.objects.create(action="Delete", model="Patient", instance=str(p),
                                                 ip=get_client_ip(request), username=request.user.username, campaign=this_campaign)
                message_content = "{0} has deleted the record for {1} from fEMR On-Chain on {2}".format(
                    request.user, p, timezone.now())
                Message.objects.create(
                    sender=request.user,
                    recipient=contact,
                    subject="WARNING! PATIENT DELETED",
                    content=message_content
                )
                Patient.objects.filter(id=p.id).delete()
            except ObjectDoesNotExist:
                pass
            return render(request, 'data/patient_deleted_success.html')
        else:
            p = get_object_or_404(Patient, pk=id)
            return render(request, 'data/delete.html', {'patient': p})
    else:
        return redirect('main:not_logged_in')
