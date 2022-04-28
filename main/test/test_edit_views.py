from django.test.client import Client

from model_bakery import baker

from main.models import fEMRUser


def test_new_diagnosis_view():
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    u.campaigns.add(c)
    u.save()
    p = baker.make("main.Patient")
    d = baker.make("main.Diagnosis")
    e = baker.make("main.PatientEncounter", patient=p, campaign=c)
    client = Client()
    client.post("/login_view/", {"username": "test", "password": "testingpassword"})
    return_response = client.post(
        f"/new_diagnosis_view/{p.id}/{e.id}", {"diagnosis": d.id}
    )
    u.delete()
    p.delete()
    d.delete()
    e.delete()
    c.delete()
    assert return_response.status_code == 200
