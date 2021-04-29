from django.shortcuts import render, redirect

from .forms import TreatmentForm, MedicationForm, DiagnosisForm, ChiefComplaintForm


def chief_complaint_form_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        if request.method == "POST":
            form = ChiefComplaintForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('main:patient_list_view')
        if request.method == "GET":
            form = ChiefComplaintForm()
        return render(request, 'forms/generic.html', {
            'form': form
        })
    else:
        return redirect('/not_logged_in')


def treatment_form_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        if request.method == "POST":
            form = TreatmentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('main:patient_list_view')
        if request.method == "GET":
            form = TreatmentForm()
        return render(request, 'forms/generic.html', {
            'form': form
        })
    else:
        return redirect('/not_logged_in')


def diagnosis_form_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        if request.method == "POST":
            form = DiagnosisForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('main:patient_list_view')
        if request.method == "GET":
            form = DiagnosisForm()
        return render(request, 'forms/generic.html', {
            'form': form
        })
    else:
        return redirect('/not_logged_in')


def medication_form_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        if request.method == "POST":
            form = MedicationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('main:patient_list_view')
        if request.method == "GET":
            form = MedicationForm()
        return render(request, 'forms/generic.html', {
            'form': form
        })
    else:
        return redirect('/not_logged_in')


def administration_schedule_form_view(request, id=None):
    if request.user.is_authenticated:
        if request.session['campaign'] == "RECOVERY MODE":
            return redirect('main:home')
        if request.method == "POST":
            form = AdministrationScheduleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('main:patient_list_view')
        if request.method == "GET":
            form = AdministrationScheduleForm()
        return render(request, 'forms/generic.html', {
            'form': form
        })
    else:
        return redirect('/not_logged_in')
