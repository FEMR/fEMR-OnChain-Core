"""
Defines a createadmin command extending manage.py.
"""
import os

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from main.models import fEMRUser, Instance, Campaign
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
            instance = Instance.objects.create(name="Test")
            if os.environ.get("QLDB_ENABLED") == "TRUE":
                create_tables()
        else:
            instance = Instance.objects.get(name="Test")
        if not Campaign.objects.filter(name="Test").exists():
            campaign = Campaign.objects.create(name="Test", instance=instance)
        else:
            campaign = Campaign.objects.get(name="Test")
        if not fEMRUser.objects.filter(username="admin").exists():
            superuser = fEMRUser.objects.create_superuser(
                "admin", "admin@admin.com", "OnChain-Admin"
            )
            superuser.first_name = "Admin"
            superuser.last_name = "User"
            superuser.campaigns.add(campaign)
            superuser.user_permissions.add(Permission.objects.get(name="Can add state"))
            superuser.user_permissions.add(
                Permission.objects.get(name="Can add diagnosis")
            )
            superuser.user_permissions.add(
                Permission.objects.get(name="Can add chief complaint")
            )
            superuser.user_permissions.add(
                Permission.objects.get(name="Can add medication")
            )
            superuser.save()
            Group.objects.get(name="fEMR Admin").user_set.add(superuser)
            Group.objects.get(name="Organization Admin").user_set.add(superuser)
            Group.objects.get(name="Clinician").user_set.add(superuser)
            Group.objects.get(name="Operation Admin").user_set.add(superuser)
            Group.objects.get(name="Campaign Manager").user_set.add(superuser)
            Group.objects.get(name="Developer").user_set.add(superuser)
            instance.main_contact = superuser
            instance.save()
        else:
            for user in fEMRUser.objects.all().iterator():
                user.user_permissions.add(Permission.objects.get(name="Can add state"))
                user.user_permissions.add(
                    Permission.objects.get(name="Can add diagnosis")
                )
                user.user_permissions.add(
                    Permission.objects.get(name="Can add chief complaint")
                )
                user.user_permissions.add(
                    Permission.objects.get(name="Can add medication")
                )
                user.user_permissions.add(
                    Permission.objects.get(name="Can add administration schedule")
                )
                user.user_permissions.add(
                    Permission.objects.get(name="Can add inventory category")
                )
                user.user_permissions.add(
                    Permission.objects.get(name="Can add inventory form")
                )
                user.user_permissions.add(
                    Permission.objects.get(name="Can add manufacturer")
                )
