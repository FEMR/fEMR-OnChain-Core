from dal import autocomplete

from .models import Medication, ChiefComplaint, Diagnosis


class DiagnosisAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Diagnosis.objects.none()

        qs = Diagnosis.objects.all()

        if self.q:
            qs = qs.filter(text__istartswith=self.q)
        
        return qs


class ChiefComplaintAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ChiefComplaint.objects.none()

        qs = ChiefComplaint.objects.all()

        if self.q:
            qs = qs.filter(text__istartswith=self.q)
        
        return qs


class MedicationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Medication.objects.none()

        qs = Medication.objects.all()

        if self.q:
            qs = qs.filter(text__istartswith=self.q)
        
        return qs