from django.test.client import Client
from model_bakery import baker
from main.models import fEMRUser


def test_patient_list_view():
    u = fEMRUser.objects.create_user(
        username="testhome",
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
    client.post("/login_view/", {"username": "testhome", "password": "testingpassword"})
    return_response = client.post("/patient_list_view/")
    u.delete()
    assert return_response.status_code == 200
