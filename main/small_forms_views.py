from django.shortcuts import render, redirect

from main.decorators import in_recovery_mode, is_authenticated

from .forms import TreatmentForm, MedicationForm, DiagnosisForm, ChiefComplaintForm


@in_recovery_mode
@is_authenticated
def chief_complaint_form_view(request):
    if request.method == "POST":
        form = ChiefComplaintForm(request.POST)
        if form.is_valid():
            form.save()
            return_response = redirect("main:patient_list_view")
        else:
            return_response = render(request, "forms/generic.html", {"form": form})
    else:
        return_response = render(
            request, "forms/generic.html", {"form": ChiefComplaintForm()}
        )
    return return_response


@in_recovery_mode
@is_authenticated
def treatment_form_view(request):
    if request.method == "POST":
        form = TreatmentForm(request.POST)
        if form.is_valid():
            form.save()
            return_response = redirect("main:patient_list_view")
        else:
            return_response = render(request, "forms/generic.html", {"form": form})
    else:
        return_response = render(
            request, "forms/generic.html", {"form": TreatmentForm()}
        )
    return return_response


@in_recovery_mode
@is_authenticated
def diagnosis_form_view(request):
    if request.method == "POST":
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            form.save()
            return_response = redirect("main:patient_list_view")
        else:
            return_response = render(request, "forms/generic.html", {"form": form})
    else:
        return_response = render(
            request, "forms/generic.html", {"form": DiagnosisForm()}
        )
    return return_response


@in_recovery_mode
@is_authenticated
def medication_form_view(request):
    if request.method == "POST":
        form = MedicationForm(request.POST)
        if form.is_valid():
            form.save()
            return_response = redirect("main:patient_list_view")
        else:
            return_response = render(request, "forms/generic.html", {"form": form})
    else:
        return_response = render(
            request, "forms/generic.html", {"form": MedicationForm()}
        )
    return return_response
