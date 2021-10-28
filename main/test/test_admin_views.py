from django.contrib.auth.models import Group, AnonymousUser
from django.test.client import Client, RequestFactory
from django.urls import reverse
from model_bakery import baker

from main.admin_views import admin_home
from main.models import fEMRUser


def test_admin_home_redirect():
    factory = RequestFactory()
    request = factory.get("/superuser_home")
    request.user = fEMRUser.objects.get(pk=1)
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.remove(
        request.user
    )
    response = admin_home(request)
    assert response.status_code == 302


def test_admin_home_redirect_anonymous_user():
    factory = RequestFactory()
    request = factory.get("/superuser_home")
    request.user = AnonymousUser()
    response = admin_home(request)
    assert response.status_code == 302


def test_campaign_manager_account_reset():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    v = fEMRUser.objects.create_user(
        username="test2",
        password="testingpassword",
        email="logintestinguseremail2@email.com",
    )
    u.change_password = False
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    response = client.get(reverse("main:reset_lockouts", kwargs={"username": "test2"}))
    print(response.content)
    u.delete()
    v.delete()
    assert response.status_code == 200
    assert "test2\\'s account has been reset successfully." in str(response.content)
