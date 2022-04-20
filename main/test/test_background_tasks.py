from django.contrib.auth.models import Group
from main.background_tasks import assign_broken_patient, check_admin_permission
from main.models import Patient, fEMRUser
from model_bakery import baker
from main.background_tasks import check_admin_permission
from main.models import fEMRUser


def test_check_admin_permission_false():
    u = fEMRUser.objects.create_user(
        username="test_admin_permission_false",
        password="testpassword",
        email="checkadmin1@test.com",
    )
    assert not check_admin_permission(u)
    u.delete()


def test_check_admin_permission_true():
    u = fEMRUser.objects.create_user(
        username="test_admin_permission_true",
        password="testpassword",
        email="checkadmin2@test.com",
    )
    g = Group.objects.get_or_create(name="fEMR Admin")[0]
    g.user_set.add(u)
    assert check_admin_permission(u)
    u.delete()
    g.delete()


def test_assign_broken_patient():
    for _ in range(100):
        baker.make("main.Patient")
    assert Patient.objects.filter(campaign_key=None).exists()
    assign_broken_patient()
    assert not Patient.objects.filter(campaign_key=None).exists()
    Patient.objects.all().delete()
