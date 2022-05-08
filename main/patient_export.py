from django.shortcuts import render, get_object_or_404
from silk.profiling.profiler import silk_profile
from main.decorators import in_recovery_mode, is_authenticated

from main.models import (
    Campaign,
    HistoryOfPresentIllness,
    Patient,
    PatientDiagnosis,
    Vitals,
    Treatment,
)


@silk_profile("patient-export-view-get")
def __patient_export_view_get(request, patient_id=None):
    patient = get_object_or_404(Patient, pk=patient_id)
    encounters = patient.patientencounter_set.order_by("-timestamp")
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
        history_of_present_illness_dictionary[encounter] = list(
            HistoryOfPresentIllness.objects.filter(encounter=encounter)
        )
        prescriptions[encounter] = Treatment.objects.filter(encounter=encounter)
        vitals_dictionary[encounter] = Vitals.objects.filter(encounter=encounter)
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
                name=request.user.current_campaign
            ).telehealth,
            "units": Campaign.objects.get(name=request.user.current_campaign).units,
        },
    )


@is_authenticated
@in_recovery_mode
@silk_profile("patient-export-view")
def patient_export_view(request, patient_id=None):
    return __patient_export_view_get(request, patient_id)
