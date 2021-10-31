from django.contrib.auth.models import Group
from main.background_tasks import assign_broken_patient, check_admin_permission
from main.models import Patient, fEMRUser
from model_bakery import baker
from main.background_tasks import check_admin_permission, reassign_admin_groups
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


def test_reassign_admin_groups_none_exists():
    g = Group.objects.get_or_create(name="Admin")[0]
    h = Group.objects.get_or_create(name="Campaign Manager")[0]
    u = fEMRUser.objects.create_user(
        username="reassigntestuser",
        password="somegarbagepassword",
        email="reassigntestuser@test.com",
    )
    reassign_admin_groups(u)
    assert not Group.objects.filter(name="Admin").exists()
    u.delete()
    g.delete()
    h.delete()


def test_reassign_admin_groups_exist():
    g = Group.objects.get_or_create(name="Admin")[0]
    h = Group.objects.get_or_create(name="Campaign Manager")[0]
    u = fEMRUser.objects.create_user(
        username="reassigntestuser",
        password="somegarbagepassword",
        email="reassigntestuser@test.com",
    )
    u.groups.add(g)
    reassign_admin_groups(u)
    assert u.groups.filter(name="Campaign Manager").exists()
    assert not Group.objects.filter(name="Admin").exists()
    u.delete()
    g.delete()
    h.delete()


def test_reassign_admin_groups_multiple():
    g = Group.objects.get_or_create(name="Admin")[0]
    h = Group.objects.get_or_create(name="Campaign Manager")[0]
    u = fEMRUser.objects.create_user(
        username="reassigntestuser",
        password="somegarbagepassword",
        email="reassigntestuser@test.com",
    )
    v = fEMRUser.objects.create_user(
        username="anothertestuser",
        password="anotherbadpassword",
        email="anothertestuser@test.com",
    )
    u.groups.add(g)
    v.groups.add(g)
    reassign_admin_groups(u)
    assert u.groups.filter(name="Campaign Manager").exists()
    assert Group.objects.filter(name="Admin").exists()
    u.delete()
    v.delete()
    g.delete()
    h.delete()


def test_reassign_admin_groups_no_admin_group():
    u = fEMRUser.objects.create_user(
        username="reassigntestuser",
        password="somegarbagepassword",
        email="reassigntestuser@test.com",
    )
    reassign_admin_groups(u)
    assert not Group.objects.filter(name="Admin").exists()
    assert not u.groups.filter(name="Admin").exists()
    u.delete()
