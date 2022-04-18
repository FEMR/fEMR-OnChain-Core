from django.test.client import Client
from model_bakery import baker
from main.models import Treatment, fEMRUser


def test_delete_treatment_view():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    u.campaigns.add(c)
    u.save()
    t = baker.make("main.Treatment")
    assert len(Treatment.objects.all()) == 1
    client = Client()
    client.post("/login_view/", {"username": "test", "password": "testingpassword"})
    return_response = client.get(f"/delete_treatment_view/{t.id}")
    assert len(Treatment.objects.all()) == 0
    u.delete()
    t.delete()
    c.delete()
    assert return_response.status_code == 302
