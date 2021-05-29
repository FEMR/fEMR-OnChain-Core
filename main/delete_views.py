"""
View functions handling displaying data models as sortable, filterable lists.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from .models import Patient


def patient_delete_view(request, id=None):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            data = Patient.objects.all()
            try:
                p = get_object_or_404(Patient, pk=id)
                Patient.objects.filter(id=p.id).delete()
            except ObjectDoesNotExist:
                pass
            return render(request, 'list/patient.html',
                          {'user': request.user,
                           'list_view': data})
        else:
            p = get_object_or_404(Patient, pk=id)
            return render(request, 'data/delete.html', {'patient': p})
    else:
        return redirect('main:not_logged_in')
