from django.test.client import Client
from model_bakery import baker

from main.models import fEMRUser


def test_login_view():
    u = fEMRUser.objects.create_user(username="test", password="testingpassword", email="logintestinguseremail@email.com")
    u.change_password = False
    u.save()
    client = Client()
    response = client.post('/login_view/', {'username': 'test', 'password': 'testingpassword'})
    assert response.status_code == 302
    assert response.url == "/home/"
    u.delete()


def test_logout_with_campaigns():
    u = fEMRUser.objects.create_user(username="test", password="testingpassword", email="logintestinguseremail@email.com")
    u.change_password = False
    c = baker.make('main.Campaign')
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    campaign_list = u.campaigns.filter(active=True)
    assert len(campaign_list) != 0
    client = Client()
    client.post('/login_view/', {'username': 'test', 'password': 'testingpassword'})
    response = client.post('/logout/')
    assert response.status_code == 302
    assert response.url == "/login_view/"
    u.delete()


def test_logout_no_campaigns():
    u = fEMRUser.objects.create_user(username="test", password="testingpassword", email="logintestinguseremail@email.com")
    u.change_password = False
    u.save()
    client = Client()
    response = client.post('/logout/')
    assert response.status_code == 302
    assert response.url == "/login_view/"
    u.delete()


def test_required_password_change():
    u = fEMRUser.objects.create_user(username="test2", password="testingpassword", email="logintestinguseremail2@email.com")
    u.change_password = True
    u.save()
    client = Client()
    response = client.post('/login_view/', {'username': 'test2', 'password': 'testingpassword'})
    assert response.status_code == 302
    assert response.url == "/required_change_password/"
    u.delete()


def test_login_view_with_remember_me():
    u = fEMRUser.objects.create_user(username="test", password="testingpassword", email="logintestinguseremail@email.com")
    u.change_password = False
    u.save()
    client = Client()
    response = client.post('/login_view/', {'username': 'test', 'password': 'testingpassword', 'remember_me': True})
    assert response.status_code == 302
    assert response.url == "/home/"
    assert response.client.cookies['username'].value == 'test'
    u.delete()
