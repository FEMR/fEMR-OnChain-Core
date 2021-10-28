"""
Responsible for defining endpoints relevant to data interchange through a RESTful API.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""

from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework import viewsets

from .api_permissions import IsAdmin, IsfEMRAdmin, IsAPIAllowed
from .models import (
    fEMRUser,
    Patient,
    PatientEncounter,
    MessageOfTheDay,
    Campaign,
    Instance,
    Race,
    State,
    Ethnicity,
    Organization,
    ChiefComplaint,
    AdministrationSchedule,
    Diagnosis,
    Medication,
    Test,
    Photo,
    HistoryOfPresentIllness,
    Vitals,
    PatientDiagnosis,
    Treatment,
    InventoryForm,
    InventoryCategory,
    Manufacturer,
    InventoryEntry,
    Inventory,
    UnitsSetting,
)
from .serializers import (
    UserSerializer,
    GroupSerializer,
    PatientSerializer,
    PatientEncounterSerializer,
    MessageOfTheDaySerializer,
    CampaignSerializer,
    InstanceSerializer,
    RaceSerializer,
    StateSerializer,
    EthnicitySerializer,
    OrganizationSerializer,
    ChiefComplaintSerializer,
    AdministrationScheduleSerializer,
    DiagnosisSerializer,
    MedicationSerializer,
    TestSerializer,
    PhotoSerializer,
    HistoryOfPresentIllnessSerializer,
    VitalsSerializer,
    PatientDiagnosisSerializer,
    TreatmentSerializer,
    InventoryFormSerializer,
    InventoryCategorySerializer,
    ManufacturerSerializer,
    InventoryEntrySerializer,
    InventorySerializer,
    UnitsSettingSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = fEMRUser.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, IsAPIAllowed]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, IsAPIAllowed]


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class PatientEncounterViewSet(viewsets.ModelViewSet):
    queryset = PatientEncounter.objects.all()
    serializer_class = PatientEncounterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsfEMRAdmin, IsAPIAllowed]


class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsfEMRAdmin, IsAPIAllowed]


class RaceViewSet(viewsets.ModelViewSet):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class EthnicityViewSet(viewsets.ModelViewSet):
    queryset = Ethnicity.objects.all()
    serializer_class = EthnicitySerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class ChiefComplaintViewSet(viewsets.ModelViewSet):
    queryset = ChiefComplaint.objects.all()
    serializer_class = ChiefComplaintSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class AdministrationScheduleViewSet(viewsets.ModelViewSet):
    queryset = AdministrationSchedule.objects.all()
    serializer_class = AdministrationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class HistoryOfPresentIllnessViewSet(viewsets.ModelViewSet):
    queryset = HistoryOfPresentIllness.objects.all()
    serializer_class = HistoryOfPresentIllnessSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class VitalsViewSet(viewsets.ModelViewSet):
    queryset = Vitals.objects.all()
    serializer_class = VitalsSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class PatientDiagnosisViewSet(viewsets.ModelViewSet):
    queryset = PatientDiagnosis.objects.all()
    serializer_class = PatientDiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class TreatmentViewSet(viewsets.ModelViewSet):
    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class InventoryFormViewSet(viewsets.ModelViewSet):
    queryset = InventoryForm.objects.all()
    serializer_class = InventoryFormSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class InventoryCategoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryCategory.objects.all()
    serializer_class = InventoryCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class InventoryEntryViewSet(viewsets.ModelViewSet):
    queryset = InventoryEntry.objects.all()
    serializer_class = InventoryEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


# noinspection PyUnresolvedReferences
class UnitsSettingViewSet(viewsets.ModelViewSet):
    queryset = UnitsSetting.objects.all()
    serializer_class = UnitsSettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]


# noinspection PyUnresolvedReferences
class MessageOfTheDayViewSet(viewsets.ModelViewSet):
    queryset = MessageOfTheDay.objects.all()
    serializer_class = MessageOfTheDaySerializer
    permission_classes = [permissions.IsAuthenticated, IsAPIAllowed]
