"""
Defines a createadmin command extending manage.py.
"""

from django.core.management.base import BaseCommand

from main.models import AdministrationSchedule

OPTIONS = [
    ["BID", 2],
    ["BIW", (2/7)],
    ["HS", 1],
    ["q12", 2],
    ["q24", 1],
    ["q4-6", 6],
    ["q4", 6],
    ["q6", 4],
    ["q8", 1],
    ["qAM", 1],
    ["qd", 1],
    ["qHS", 1],
    ["QID", 4],
    ["q5min", 288],
    ["qOd", (1/2)],
    ["qPM", 1],
    ["qWeek", 1],
    ["TID", 3],
    ["TIW", (3/7)],
    ["prn", 5],
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
        AdministrationSchedule.objects.filter(modifier=0.0).delete()
        for option in OPTIONS:
            a = AdministrationSchedule.objects.get_or_create(text=option[0])
            a.modifier = option[1]
            a.save()
