from django.contrib.auth.models import Group
from django.test.client import Client, RequestFactory
from model_bakery import baker
from main.models import Campaign, fEMRUser

from main.views import healthcheck


def test_healthcheck():
    factory = RequestFactory()
    request = factory.get("/healthcheck")
    return_response = healthcheck(request)
    assert return_response.status_code, 200


def test_home_view():
    u = fEMRUser.objects.create_user(
        username="testhomeview",
        password="testingpassword",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    client.post(
        "/login_view/", {"username": "testhomeview", "password": "testingpassword"}
    )
    return_response = client.post("/home/")
    u.delete()
    assert return_response.status_code == 200
    assert "Home" in str(return_response.content)


def test_home_view_recovery_mode():
    u = fEMRUser.objects.create_user(
        username="testhome",
        password="testingpassword",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = False
    c.save()
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    u.campaigns.add(c)
    u.save()
    client = Client()
    client.post("/login_view/", {"username": "testhome", "password": "testingpassword"})
    return_response = client.post("/home/")
    u.delete()
    assert return_response.status_code == 200
    assert "RECOVERY MODE" in str(return_response.content)


def test_home_view_wrong_current_campaign():
    u = fEMRUser.objects.create_user(
        username="testhomeview",
        password="testingpassword",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.current_campaign = "Test"
    u.save()
    client = Client()
    client.post(
        "/login_view/", {"username": "testhomeview", "password": "testingpassword"}
    )
    return_response = client.post("/home/")
    u.delete()
    assert return_response.status_code == 200
    assert "Home" in str(return_response.content)


def test_switch_campaign():
    u = fEMRUser.objects.create_user(
        username="testswitchcampaign",
        password="testingpassword",
        email="switchcampaigntestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    u.campaigns.add(c)
    u.campaigns.add(Campaign.objects.create(name="Test", instance=c.instance))
    u.current_campaign = "Test"
    u.save()
    client = Client()
    client.post(
        "/login_view/",
        {"username": "testswitchcampaign", "password": "testingpassword"},
    )
    return_response = client.post("/home/")
    assert return_response.status_code == 200
    assert u.current_campaign == "Test"
    client.post("/change_campaign/", {"campaign": c.name})
    return_response = client.post("/home/")
    u = fEMRUser.objects.get(username="testswitchcampaign")
    campaign = u.current_campaign
    u.delete()
    assert return_response.status_code == 200
    print(campaign)
    assert campaign == c.name
