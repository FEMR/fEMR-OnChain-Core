from django.contrib.auth.models import Group
from django.test.client import Client
from model_bakery import baker

from main.models import fEMRUser


def test_edit_organization_when_contact_null():
    fEMRUser.objects.all().delete()
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
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
    o = baker.make("main.Organization")
    return_response = client.get("/edit_organization/{0}".format(o.id))
    assert return_response.status_code == 200
    assert "contact_edit_form_div" not in str(return_response.content)
    assert "contact_edit_form_activate" not in str(return_response.content)
    u.delete()
    c.delete()
