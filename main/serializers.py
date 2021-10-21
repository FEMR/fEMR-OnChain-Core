"""
Serializer objects defining what fields of each model should be exposed to the API.
"""
from django.contrib.auth.models import Group
from rest_framework import serializers

from main.models import fEMRUser, Patient, PatientEncounter, Instance, Campaign, Race, State, Ethnicity, Organization, \
    ChiefComplaint, AdministrationSchedule, Diagnosis, Medication, MessageOfTheDay, UnitsSetting, Inventory, \
    InventoryEntry, Manufacturer, InventoryCategory, InventoryForm, Treatment, PatientDiagnosis, Vitals, \
    HistoryOfPresentIllness, Photo, Test


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes the `fEMRUser` model for API consumption.
    """

    class Meta:
        """
        Serializer meta class.
        """
        model = fEMRUser
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializes the `django.contrib.auth.models.Group` model for API consumption.
    """

    class Meta:
        """
        Serializer meta class.
        """
        model = Group
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializes the `Patient` model for API consumption.
    """

    class Meta:
        """
        Serializer meta class.
        """
        model = Patient
        fields = '__all__'


class PatientEncounterSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = PatientEncounter
        fields = '__all__'


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Instance
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Campaign
        fields = '__all__'


class RaceSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Race
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = State
        fields = '__all__'


class EthnicitySerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Ethnicity
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Organization
        fields = '__all__'


class ChiefComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = ChiefComplaint
        fields = '__all__'


class AdministrationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = AdministrationSchedule
        fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Diagnosis
        fields = '__all__'


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Medication
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Test
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Photo
        fields = '__all__'


class HistoryOfPresentIllnessSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = HistoryOfPresentIllness
        fields = '__all__'


class VitalsSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Vitals
        fields = '__all__'


class PatientDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = PatientDiagnosis
        fields = '__all__'


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Treatment
        fields = '__all__'


class InventoryFormSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = InventoryForm
        fields = '__all__'


class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = InventoryCategory
        fields = '__all__'


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Manufacturer
        fields = '__all__'


class InventoryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = InventoryEntry
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = Inventory
        fields = '__all__'


class UnitsSettingSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = UnitsSetting
        fields = '__all__'


class MessageOfTheDaySerializer(serializers.ModelSerializer):
    class Meta:
        """
        Serializer meta class.
        """
        model = MessageOfTheDay
        fields = '__all__'
