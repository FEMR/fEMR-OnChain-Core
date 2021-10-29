from django.test.client import Client
from main.models import fEMRUser


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
        "/login_view/", {"username": "test", "password": "testinglockout"}
    )
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testinglockout"}
    )
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testinglockout"}
    )
    return_response = client.post(
        "/login_view/", {"username": "test", "password": "testinglockout"}
    )
    u.delete()
    assert return_response.status_code == 403
    assert (
        "Too many access attempts. Try again in 15 minutes or contact your Campaign Manager."
        in str(return_response.content)
    )
