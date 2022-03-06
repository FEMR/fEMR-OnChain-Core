from dal import autocomplete
from silk.profiling.profiler import silk_profile

from .models import (
    Campaign,
    Ethnicity,
    InventoryCategory,
    InventoryEntry,
    InventoryForm,
    Manufacturer,
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


class InventoryEntryAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_result_label(self, result):
        return str(result)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return InventoryEntry.objects.none()

        campaign = Campaign.objects.get(name=self.request.session["campaign"])
        autocomplete_queryset = campaign.inventory.entries.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(
                medication__text__icontains=self.q
            )

        return autocomplete_queryset


class InventoryFormAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return InventoryForm.objects.none()

        autocomplete_queryset = InventoryForm.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(name__icontains=self.q)

        return autocomplete_queryset


class InventoryCategoryAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return InventoryCategory.objects.none()

        autocomplete_queryset = InventoryCategory.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(name__icontains=self.q)

        return autocomplete_queryset


class ManufacturerAutocomplete(
    autocomplete.Select2QuerySetView
):  # pylint: disable=too-many-ancestors
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Manufacturer.objects.none()

        autocomplete_queryset = Manufacturer.objects.all()

        if self.q:
            autocomplete_queryset = autocomplete_queryset.filter(name__icontains=self.q)

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
