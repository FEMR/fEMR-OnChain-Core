"""
Defines a createadmin command extending manage.py.
"""

from django.core.management.base import BaseCommand

from main.models import Campaign, Ethnicity, Race

R_OPTIONS = [
    "Native American or Native Alaskan",
    "Asian",
    "Black, African American",
    "Hispanic or Latinx",
    "Mixed Race",
    "White",
    "Nondisclosed",
]
E_OPTIONS = [
    "Hispanic or Latinx",
    "Not Hispanic or Latinx",
    "Nondisclosed",
]


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
        campaign = Campaign.objects.get(name="Test")
        for option in R_OPTIONS:
            if not Race.objects.filter(name=option).exists():
                r = Race.objects.create(name=option)
                campaign.race_options.add(r)

        for option in E_OPTIONS:
            if not Ethnicity.objects.filter(name=option).exists():
                e = Ethnicity.objects.create(name=option)
                campaign.ethnicity_options.add(e)
        campaign.save()
