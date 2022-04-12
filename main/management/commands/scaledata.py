"""
Defines a createadmin command extending manage.py.
"""

from django.core.management.base import BaseCommand
from main.models import Campaign, Patient
from model_bakery import baker


class Command(BaseCommand):
    """
    Extends the BaseCommand class, providing tie-ins to Django.
    """

    def handle(self, *args, **options):
        """
        Carry out the command functionality.

        @param args:
        @param options:
        @return:
        """
        campaign = Campaign.objects.get_or_create("Test")[0]
        if Patient.objects.filter(campaign=campaign).count() == 0:
            print("Generating patient data.")
            for p in range(1000):
                patient = baker.make("main.Patient")
                patient.campaign.add(campaign)
                for _ in range(10):
                    encounter = baker.make("main.PatientEncounter")
                    encounter.patient = patient
                    encounter.campaign = campaign
                    encounter.save()
                print(f"Patient {p} finished.")
        else:
            print("Database already populated.")
