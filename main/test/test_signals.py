from django.test.client import Client
from model_bakery import baker
from clinic_messages.models import Message
from main.models import fEMRUser


def test_axes_lockout_signal_view():
    fEMRUser.objects.all().delete()
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.change_password = False
    u.save()
    client = Client()
    for _ in range(4):
        return_response = client.post(
            "/login_view/", {"username": "test", "password": "testinglockout"}
        )
    u.delete()

    assert return_response.status_code == 403
    assert (
        "Too many access attempts. Try again in 15 minutes or contact your Campaign Manager."
        in str(return_response.content)
    )


def test_axes_lockout_sends_message():
    fEMRUser.objects.all().delete()
    c = baker.make("main.Campaign")
    a = fEMRUser.objects.create_superuser(
        username="admin",
        password="admintestpassword",
        email="admin@test.com",
    )
    u = fEMRUser.objects.create_user(
        username="test",
        password="testingpassword",
        email="logintestinguseremail@email.com",
    )
    u.campaigns.add(c)
    u.change_password = False
    u.save()
    v = fEMRUser.objects.create_user(
        username="test2",
        password="testingpassword",
        email="logintestinguseremail2@email.com",
    )
    v.campaigns.add(c)
    v.change_password = False
    v.save()
    c.main_contact = u
    c.save()
    assert len(v.campaigns.all()) == 1
    assert len(Message.objects.all()) == 0
    assert len(Message.objects.filter(recipient=u)) == 0
    client = Client()
    for _ in range(3):
        client.post("/login_view/", {"username": "test2", "password": "testinglockout"})
    assert len(Message.objects.all()) == 1
    assert len(Message.objects.filter(recipient=u)) == 1
    Message.objects.all().delete()
    c.delete()
    u.delete()
    v.delete()
    a.delete()
