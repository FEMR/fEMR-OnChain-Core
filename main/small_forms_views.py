from django.shortcuts import render, redirect

from .forms import TreatmentForm, MedicationForm, DiagnosisForm, ChiefComplaintForm


def chief_complaint_form_view(request):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
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
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def treatment_form_view(request):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
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
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def diagnosis_form_view(request):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
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
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def medication_form_view(request):
    if request.user.is_authenticated:
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        elif request.method == "POST":
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
    else:
        return_response = redirect("/not_logged_in")
    return return_response
