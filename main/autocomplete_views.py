from dal import autocomplete
from silk.profiling.profiler import silk_profile

from .models import Ethnicity, Medication, ChiefComplaint, Diagnosis, AdministrationSchedule, Race, State, Test


class DiagnosisAutocomplete(autocomplete.Select2QuerySetView):
    @silk_profile('diagnosis-autocomplete')
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Diagnosis.objects.none()

        qs = Diagnosis.objects.all()

        if self.q:
            qs = qs.filter(text__icontains=self.q)

        return qs


class ChiefComplaintAutocomplete(autocomplete.Select2QuerySetView):
    @silk_profile('chief-complaint-autocomplete')
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ChiefComplaint.objects.none()

        qs = ChiefComplaint.objects.filter(active=True)

        if self.q:
            qs = qs.filter(text__icontains=self.q)

        return qs


class MedicationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Medication.objects.none()

        qs = Medication.objects.all()

        if self.q:
            qs = qs.filter(text__icontains=self.q)

        return qs


class TestAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Test.objects.none()

        qs = Test.objects.all()

        if self.q:
            qs = qs.filter(text__icontains=self.q)

        return qs


class AdministrationScheduleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return AdministrationSchedule.objects.none()

        qs = AdministrationSchedule.objects.all()

        if self.q:
            qs = qs.filter(text__icontains=self.q)

        return qs


class RaceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Race.objects.none()

        qs = Race.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class EthnicityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Ethnicity.objects.none()

        qs = Ethnicity.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class StateAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return State.objects.none()

        qs = State.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
