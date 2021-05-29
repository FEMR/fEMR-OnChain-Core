"""
View functions handling displaying data models as sortable, filterable lists.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from .models import Allergy, Immunization, Procedure, Medication, LabTest, Test, Patient, HealthConcern, Problem


def allergy_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = Allergy.objects.all()
        try:
            p = get_object_or_404(Allergy, pk=id)
            Allergy.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/allergy.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def immunization_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = Immunization.objects.all()
        try:
            p = get_object_or_404(Immunization, pk=id)
            Immunization.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/immunization.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def problem_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = Problem.objects.all()
        try:
            p = get_object_or_404(Problem, pk=id)
            Problem.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/problem.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def procedure_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = Procedure.objects.all()
        try:
            p = get_object_or_404(Procedure, pk=id)
            Procedure.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/procedure.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def medication_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = Medication.objects.all()
        try:
            p = get_object_or_404(Medication, pk=id)
            Medication.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/medication.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def lab_test_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = LabTest.objects.all()
        try:
            p = get_object_or_404(LabTest, pk=id)
            LabTest.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/lab_test.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


def test_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = Test.objects.all()
        try:
            p = get_object_or_404(Test, pk=id)
            Test.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/test.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')


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


def health_concern_delete_view(request):
    """
    Delete function.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        data = HealthConcern.objects.all()
        try:
            p = get_object_or_404(HealthConcern, pk=id)
            HealthConcern.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/health_concern.html',
                      {'user': request.user,
                       'list_view': data})
    else:
        return redirect('main:not_logged_in')
