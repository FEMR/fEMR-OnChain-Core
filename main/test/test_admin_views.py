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
    u.delete()
    c.delete()
    assert return_response.status_code == 200
    assert "Campaigns" in str(return_response.content)


def test_error_on_creating_user_with_existing_username():
    l = fEMRUser.objects.create_user(
        username="createusertestuser",
        password="testingpassword",
        email="anothertestuseremail@email.com",
    )
    u = fEMRUser.objects.create_user(
        username="createusertest",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    g = Group.objects.get_or_create(name="Clinician")[0]
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.add(u)
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    return_response = client.post(
        "/login_view/", {"username": "createusertest", "password": "testingpassword"}
    )
    return_response = client.post(
        "/create_user_view/",
        {
            "campaigns": [str(c.id)],
            "email": "testuser@test.com",
            "first_name": "Test",
            "groups": [str(g.id)],
            "last_name": "User",
            "password1": "testingpassword",
            "password2": "testingpassword",
            "username": "createusertestuser",
        },
    )
    u.delete()
    l.delete()
    c.delete()
    assert return_response.status_code == 200
    assert "A user with that username already exists." in str(return_response.content)


def test_create_user():
    u = fEMRUser.objects.create_user(
        username="createusertest",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    g = Group.objects.get_or_create(name="Clinician")[0]
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.add(u)
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    return_response = client.post(
        "/login_view/", {"username": "createusertest", "password": "testingpassword"}
    )
    return_response = client.post(
        "/create_user_view/",
        {
            "campaigns": [str(c.id)],
            "email": "createtestuser@test.com",
            "first_name": "Test",
            "groups": [str(g.id)],
            "last_name": "User",
            "password1": "testingpassword",
            "password2": "testingpassword",
            "username": "createusertestusersuccess",
        },
    )
    u.delete()
    c.delete()
    assert return_response.status_code == 200
    assert "Changes successfully submitted." in str(return_response.content)


def test_filter_audit_logs_view():
    u = fEMRUser.objects.create_user(
        username="testfilterauditlogsview",
        password="testingpassword",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    Group.objects.get_or_create(name="Clinician")[0]
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.add(u)
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    client.post(
        "/login_view/",
        {"username": "testfilterauditlogsview", "password": "testingpassword"},
    )
    return_response = client.get(
        path="/filter_audit_logs_view/",
        data={
            "filter_list": "2",
            "date_filter_day": "",
            "date_filter_start": "",
            "date_filter_end": "",
        },
    )
    u.delete()
    assert return_response.status_code == 200


def test_add_users_to_campaign_view():
    u = fEMRUser.objects.create_user(
        username="testadduserstocampainview",
        password="testingpassword",
        email="testadduserstocampainview@email.com",
    )
    u.change_password = False
    Group.objects.get_or_create(name="Clinician")[0]
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.add(u)
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    client.post(
        "/login_view/",
        {"username": "testadduserstocampainview", "password": "testingpassword"},
    )
    return_response = client.get(path="/add_users_to_campaign")
    u.delete()
    assert return_response.status_code == 200


def test_permission_denied_account_reset_lockouts():
    client = Client()
    return_response = client.get(
        reverse("main:reset_lockouts", kwargs={"username": "test2"})
    )
    assert return_response.status_code == 302
    assert return_response.url == "/not_logged_in/"
