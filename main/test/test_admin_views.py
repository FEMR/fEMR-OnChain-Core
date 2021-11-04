from django.contrib.auth.models import Group, AnonymousUser
from django.test.client import Client, RequestFactory
from django.urls import reverse
from model_bakery import baker

from main.admin_views import admin_home
from main.models import fEMRUser


def test_admin_home_redirect():
    factory = RequestFactory()
    request = factory.get("/superuser_home")
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    request.user = u
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.remove(
        request.user
    )
    return_response = admin_home(request)
    assert return_response.status_code == 302
    u.delete()


def test_admin_home_redirect_anonymous_user():
    factory = RequestFactory()
    request = factory.get("/superuser_home")
    request.user = AnonymousUser()
    return_response = admin_home(request)
    assert return_response.status_code == 302


def test_permission_denied_account_reset():
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
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    return_response = client.get(
        reverse("main:reset_lockouts", kwargs={"username": "test2"})
    )
    print(return_response.url)
    u.delete()
    v.delete()
    c.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/permission_denied/"


def test_success_account_reset():
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
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    return_response = client.get(
        reverse("main:reset_lockouts", kwargs={"username": "test2"})
    )
    u.delete()
    v.delete()
    c.delete()
    assert return_response.status_code == 200
    print(return_response.content)
    assert "test2\\'s account has been reset successfully." in str(
        return_response.content
    )


def test_no_success_account_reset():
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
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    return_response = client.get(reverse("main:reset_lockouts"))
    u.delete()
    v.delete()
    c.delete()
    assert return_response.status_code == 200
    assert (
        "In your ticket, let us know that you saw the error at user_reset_no_success."
        in str(return_response.content)
    )


def test_campaigns_option_on_admin_user_create():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.add(u)
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    return_response = client.get("/create_user_view/")
    print(return_response)
    u.delete()
    c.delete()
    assert return_response.status_code == 200
    assert "Campaigns" in str(return_response.content)


def test_permission_denied_account_reset():
    client = Client()
    return_response = client.get(
        reverse("main:reset_lockouts", kwargs={"username": "test2"})
    )
    assert return_response.status_code == 302
    assert return_response.url == "/not_logged_in/"
