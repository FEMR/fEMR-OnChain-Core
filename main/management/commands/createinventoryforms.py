"""
Defines a createadmin command extending manage.py.
"""

from django.core.management.base import BaseCommand

from main.models import InventoryForm

OPTIONS = [
    'liquid',
    'tablets',
    'cream',
    'supply'
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
            if not InventoryForm.objects.filter(name=option).exists():
                InventoryForm.objects.create(name=option)
