"""
Defines a createadmin command extending manage.py.
"""

from main.models import Ethnicity, Race
from django.core.management.base import BaseCommand

R_OPTIONS = [
    'Native American or Native Alaskan',
    'Asian',
    'Black, African American',
    'Hispanic or Latinx',
    'Mixed Race',
    'White',
    'Nondisclosed',
]
E_OPTIONS = [
    'Hispanic or Latinx',
    'Not Hispanic or Latinx',
    'Nondisclosed',
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
        for option in R_OPTIONS:
            if not Race.objects.filter(name=option).exists():
                Race.objects.create(name=option)

        for option in E_OPTIONS:
            if not Ethnicity.objects.filter(name=option).exists():
                Ethnicity.objects.create(name=option)
