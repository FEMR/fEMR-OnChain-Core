from django.contrib.auth.models import Group, AnonymousUser
from django.test.client import RequestFactory

from main.admin_views import admin_home
from main.models import fEMRUser


def test_admin_home_redirect():
    factory = RequestFactory()
    request = factory.get('/superuser_home')
    request.user = fEMRUser.objects.get(pk=1)
    Group.objects.get_or_create(name="Campaign Manager")[0].user_set.remove(request.user)
    response = admin_home(request)
    assert response.status_code == 302


def test_admin_home_redirect_anonymous_user():
    factory = RequestFactory()
    request = factory.get('/superuser_home')
    request.user = AnonymousUser()
    response = admin_home(request)
    assert response.status_code == 302
