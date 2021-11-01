from dal import autocomplete
from silk.profiling.profiler import silk_profile

from .models import (
    Ethnicity,
    Medication,
    ChiefComplaint,
    Diagnosis,
    AdministrationSchedule,
    Race,
    State,
    Test,
)


class DiagnosisAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Diagnosis.objects.none()

        autocomplete_queryset = Diagnosis.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(text__icontains=self.q)

        return autocomplete_queryset


class ChiefComplaintAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    @silk_profile("chief-complaint-autocomplete")
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ChiefComplaint.objects.none()

        autocomplete_queryset = ChiefComplaint.objects.filter(active=True)

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(text__icontains=self.q)

        return autocomplete_queryset


class MedicationAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Medication.objects.none()

        autocomplete_queryset = Medication.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(text__icontains=self.q)

        return autocomplete_queryset


class TestAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Test.objects.none()

        autocomplete_queryset = Test.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(text__icontains=self.q)

        return autocomplete_queryset


class AdministrationScheduleAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return AdministrationSchedule.objects.none()

        autocomplete_queryset = AdministrationSchedule.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(text__icontains=self.q)

        return autocomplete_queryset


class RaceAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Race.objects.none()

        autocomplete_queryset = Race.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(name__icontains=self.q)

        return autocomplete_queryset


class EthnicityAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Ethnicity.objects.none()

        autocomplete_queryset = Ethnicity.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(name__icontains=self.q)

        return autocomplete_queryset


class StateAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return State.objects.none()

        autocomplete_queryset = State.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(name__icontains=self.q)

        return autocomplete_queryset
