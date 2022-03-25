from django.shortcuts import render, redirect, get_object_or_404
from silk.profiling.profiler import silk_profile

from main.models import (
    Campaign,
    HistoryOfPresentIllness,
    Patient,
    PatientDiagnosis,
    PatientEncounter,
    Vitals,
    Treatment,
)


@silk_profile("patient-export-view-get")
def __patient_export_view_get(request, patient_id=None):
    patient = get_object_or_404(Patient, pk=patient_id)
    encounters = PatientEncounter.objects.filter(patient=patient).order_by("-timestamp")
    prescriptions = {}
    diagnoses = {}
    vitals_dictionary = {}
    history_of_present_illness_dictionary = {}
    for encounter in encounters:
        try:
            diagnoses[encounter] = sum(
                [
                    list(queryset.diagnosis.all())
                    for queryset in PatientDiagnosis.objects.filter(encounter=encounter)
                ],
                [],
            )
        except PatientDiagnosis.DoesNotExist:
            diagnoses[encounter] = []
        history_of_present_illness_dictionary[encounter] = list(HistoryOfPresentIllness.objects.filter(encounter=encounter))
        prescriptions[encounter] = list(Treatment.objects.filter(encounter=encounter))
        vitals_dictionary[encounter] = list(Vitals.objects.filter(encounter=encounter))
    return render(
        request,
        "export/patient_export.html",
        {
            "patient": patient,
            "encounters": encounters,
            "prescriptions": prescriptions,
            "diagnoses": diagnoses,
            "histories_of_present_illness": history_of_present_illness_dictionary,
            "vitals": vitals_dictionary,
            "telehealth": Campaign.objects.get(
                name=request.session["campaign"]
            ).telehealth,
            "units": Campaign.objects.get(name=request.session["campaign"]).units,
        },
    )


@silk_profile("patient-export-view")
def patient_export_view(request, patient_id=None):
    if request.user.is_authenticated:
        if request.session["campaign"] == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            return_response = __patient_export_view_get(request, patient_id)
    else:
        return_response = redirect("/not_logged_in")
    return return_response
