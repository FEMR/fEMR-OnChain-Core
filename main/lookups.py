from selectable.base import ModelLookup
from selectable.registry import registry

from .models import Treatment, AdministrationSchedule, Medication, Diagnosis, ChiefComplaint


class TreatmentLookup(ModelLookup):
    model = Treatment
    search_fields = ('medication__text__icontains', )


class AdministrationScheduleLookup(ModelLookup):
    model = AdministrationSchedule
    search_fields = ('text__icontains', )


class MedicationLookup(ModelLookup):
    model = Medication
    search_fields = ('text__icontains', )


class DiagnosisLookup(ModelLookup):
    model = Diagnosis
    search_fields = ('text__icontains', )


class ChiefComplaintLookup(ModelLookup):
    model = ChiefComplaint
    search_fields = ('text__icontains', )


registry.register(TreatmentLookup)
registry.register(AdministrationScheduleLookup)
registry.register(MedicationLookup)
registry.register(DiagnosisLookup)
registry.register(ChiefComplaintLookup)