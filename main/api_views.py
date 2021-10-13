"""
Responsible for defining endpoints relevant to data interchange through a RESTful API.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""

from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework import viewsets

from .api_permissions import IsAdmin, IsfEMRAdmin
from .models import Patient, fEMRUser, PatientEncounter, Instance, Campaign
from .serializers import UserSerializer, GroupSerializer, PatientSerializer, PatientEncounterSerializer, \
    InstanceSerializer, CampaignSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API Endpoint Adapter - Allergy
    """
    queryset = fEMRUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API Endpoint Adapter - Allergy
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]


class PatientEncounterViewSet(viewsets.ModelViewSet):
    queryset = PatientEncounter.objects.all()
    serializer_class = PatientEncounterSerializer
    permission_classes = [permissions.IsAuthenticated]


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsfEMRAdmin]


class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsfEMRAdmin]
