from django.contrib.auth.models import Group
from django.test.client import Client, RequestFactory
from model_bakery import baker
from main.models import fEMRUser

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
    print(return_response.content)
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
    print(return_response.content)
    assert return_response.status_code == 200
    assert "RECOVERY MODE" in str(return_response.content)
