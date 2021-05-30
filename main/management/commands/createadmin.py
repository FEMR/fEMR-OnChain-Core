"""
Defines a createadmin command extending manage.py.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from main.models import fEMRUser, Instance, Campaign, Contact
from main.qldb_interface import create_tables


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
        if not Instance.objects.filter(name="Test").exists():
            print("Populating instance table.")
            c = Contact.objects.create(
                first_name="Test",
                last_name="Contact",
                email_address="test@test.com",
                phone_number="5551234567"
            )
            instance = Instance.objects.create(name="Test", main_contact=c)
            create_tables()
        else:
            instance = Instance.objects.get(name="Test")
        if not Campaign.objects.filter(name="Test").exists():
            print("Populating campaign table.")
            campaign = Campaign.objects.create(name="Test", instance=instance)
        else:
            campaign = Campaign.objects.get(name="Test")
        if not fEMRUser.objects.filter(username="admin").exists():
            print("Populating user table.")
            superuser = fEMRUser.objects.create_superuser("admin", "admin@admin.com", "OnChain-Admin")
            superuser.first_name = "Admin"
            superuser.last_name = "User"
            superuser.campaigns.add(campaign)
            superuser.save()
            Group.objects.get(name='Admin').user_set.add(superuser)
            Group.objects.get(name='fEMR Admin').user_set.add(superuser)