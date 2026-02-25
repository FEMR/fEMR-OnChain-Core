from django.contrib.auth.models import AnonymousUser, Group
from django.test.client import Client, RequestFactory
from django.urls import reverse
from app_mr.models import SupportTicket

from app_mr.views import bug_list_view, not_logged_in
from main.models import fEMRUser

from model_bakery import baker


def test_not_logged_in():
    factory = RequestFactory()
    request = factory.get("/not_logged_in")
    return_response = not_logged_in(request)
    assert return_response.status_code == 200


def test_bug_list_view_redirect():
    factory = RequestFactory()
    request = factory.get("/bug_list_view")
    request.user = AnonymousUser()
    return_response = bug_list_view(request)
    assert return_response.status_code == 302


def test_bug_list_logged():
    u = fEMRUser.objects.create_user(
        username="testhome",
        password="testingpasswordbuglist",
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
        "/login_view/", {"username": "testhome", "password": "testingpasswordbuglist"}
    )
    return_response = client.get(
        reverse("app_mr:bug_list_view", kwargs={"ticket_type": "0"})
    )
    u.delete()
    assert return_response.status_code == 200
    assert "Leave a Bug or Problem Report" in str(return_response.content)


def test_bug_detail_view_get():
    u = fEMRUser.objects.create_user(
        username="testhome",
        password="testingpasswordbuglist",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    t = baker.make("app_mr.SupportTicket")
    t.reporter = u
    t.save()
    client = Client()
    client.post(
        "/login_view/", {"username": "testhome", "password": "testingpasswordbuglist"}
    )
    return_response = client.get(
        reverse("app_mr:bug_detail_view", kwargs={"ticket_id": t.id})
    )
    u.delete()
    assert return_response.status_code == 200
    SupportTicket.objects.all().delete()


def test_bug_detail_view():
    u = fEMRUser.objects.create_user(
        username="testhome",
        password="testingpasswordbuglist",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    t = baker.make("app_mr.SupportTicket")
    t.reporter = u
    t.save()
    Group.objects.get_or_create(name="Developer")
    client = Client()
    client.post(
        "/login_view/", {"username": "testhome", "password": "testingpasswordbuglist"}
    )
    return_response = client.post(
        reverse(
            "app_mr:bug_detail_view",
            kwargs={
                "ticket_id": t.id,
            },
        ),
        {
            "description": "Test",
            "status": "1",
            "title": "Test",
        },
    )
    u.delete()
    assert return_response.status_code == 200
    SupportTicket.objects.all().delete()


def test_bug_detail_view_get():
    u = fEMRUser.objects.create_user(
        username="testhome",
        password="testingpasswordbuglist",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    t = baker.make("app_mr.SupportTicket")
    t.title = "Test"
    t.reporter = u
    t.save()
    assert SupportTicket.objects.count() == 1
    Group.objects.get_or_create(name="Developer")
    client = Client()
    client.post(
        "/login_view/", {"username": "testhome", "password": "testingpasswordbuglist"}
    )
    return_response = client.post(
        reverse(
            "app_mr:bug_detail_view",
            kwargs={
                "ticket_id": t.id,
            },
        ),
        {
            "description": "Test",
            "status": "6",
            "title": "Test",
        },
    )
    assert return_response.status_code == 200
    print(SupportTicket.objects.all())
    t2 = SupportTicket.objects.get(title="Test")
    assert t2.active == False
    SupportTicket.objects.all().delete()
    u.delete()


def test_bug_comment_view_get():
    u = fEMRUser.objects.create_user(
        username="testcomment",
        password="testingpasswordbuglist",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    t = baker.make("app_mr.SupportTicket")
    t.title = "Test"
    t.reporter = u
    t.save()
    assert SupportTicket.objects.count() == 1
    Group.objects.get_or_create(name="Developer")
    client = Client()
    client.post(
        "/login_view/",
        {"username": "testcomment", "password": "testingpasswordbuglist"},
    )
    return_response = client.post(
        reverse(
            "app_mr:post_comment_view",
            kwargs={
                "bug_id": t.id,
            },
        ),
        {"comment": "This is a test."},
    )
    print(return_response)
    assert return_response.status_code == 200
    SupportTicket.objects.all().delete()
    u.delete()
