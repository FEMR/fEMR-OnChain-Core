from django.shortcuts import redirect, render
from django.db.models.query_utils import Q


def add_supply_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/add_supply.html')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def edit_supply_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/edit_supply.html')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def remove_supply_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/edit_supply.html')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def csv_handler_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/csv_handler.html')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def csv_import_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/csv_import.html')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def csv_export_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/csv_export.html')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')
