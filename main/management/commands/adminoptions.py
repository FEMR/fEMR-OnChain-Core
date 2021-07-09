"""
Defines a createadmin command extending manage.py.
"""

from main.models import AdministrationSchedule
from django.core.management.base import BaseCommand

OPTIONS = [
    'alt',
    'BID',
    'BIW',
    'CID',
    'HS',
    'q12',
    'q24',
    'q4-6',
    'q4',
    'q6',
    'q8',
    'qAM',
    'qd',
    'qHS',
    'QID',
    'q5min',
    'qOd',
    'qPM',
    'qWeek',
    'TID',
    'TIW'
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
        for option in OPTIONS:
            if not AdministrationSchedule.objects.filter(text=option).exists():
                AdministrationSchedule.objects.create(text=option)
