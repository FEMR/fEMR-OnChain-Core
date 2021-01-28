"""
Serializer objects defining what fields of each model should be exposed to the API.
"""
from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import fEMRUser, Patient, PatientEncounter, Instance, Campaign


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
        model = PatientEncounter
        fields = '__all__'


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
