from django.test.client import Client
from model_bakery import baker

from main.models import Campaign, fEMRUser


def test_login_view():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    u.save()
    client = Client()
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    u.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/home/"


def test_login_view_no_campaigns():
    fEMRUser.objects.all().delete()
    Campaign.objects.all().delete()
    assert len(fEMRUser.objects.all()) == 0
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    u.save()
    assert len(Campaign.objects.all()) == 0
    assert not u.groups.filter(name="fEMR Admin").exists()
    assert len(list(u.campaigns.all())) == 0
    client = Client()
    assert u.is_authenticated
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testingpassword"}
    )
    assert "campaign" not in client.session
    assert client.session.get("campaign", None) is None
    u.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/home/"


def test_login_with_campaigns():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    campaign_list = u.campaigns.filter(active=True)
    assert len(campaign_list) != 0
    client = Client()
    client.post("/login_view/", {"username": "test", "password": "testingpassword"})
    return_response = client.post("/logout/")
    u.delete()
    c.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/login_view/"


def test_login_with_inactive_campaigns():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = False
    c.save()
    u.campaigns.add(c)
    u.save()
    campaign_list = u.campaigns.filter(active=True)
    assert len(campaign_list) == 0
    client = Client()
    client.post("/login_view/", {"username": "test", "password": "testingpassword"})
    return_response = client.post("/logout/")
    u.delete()
    c.delete()
    assert return_response.status_code == 200
    assert (
        "You have no active campaigns. Please contact your administrator to proceed."
        in str(return_response.content)
    )


def test_logout_no_campaigns():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    u.save()
    client = Client()
    return_response = client.post("/logout/")
    u.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/login_view/"


def test_required_password_change():
    u = fEMRUser.objects.create_user(
        username="test2",
        password="testingpassword",
        email="logintestinguseremail2@email.com",
    )
    u.change_password = True
    u.save()
    client = Client()
    return_response = client.post(
        "/login_view/", {"username": "test2", "password": "testingpassword"}
    )
    u.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/required_change_password/"


def test_login_view_with_remember_me():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    u.save()
    client = Client()
    return_response = client.post(
        "/login_view/",
        {"username": "test", "password": "testingpassword", "remember_me": True},
    )
    u.delete()
    assert return_response.status_code == 302
    assert return_response.url == "/home/"
    assert return_response.client.cookies["username"].value == "test"
