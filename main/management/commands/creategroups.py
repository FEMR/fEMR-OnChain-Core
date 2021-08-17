"""
Defines a createadmin command extending manage.py.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

GROUPS = [
    'Admin',
    'fEMR Admin',
    'Clinician',
    'Operation Admin',
    'Campaign Manager'
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
        for group in GROUPS:
            if not Group.objects.filter(name=group).exists():
                Group.objects.create(name=group)
