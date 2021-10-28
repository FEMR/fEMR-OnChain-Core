from django.contrib.auth.models import Group
from django.test.client import Client
from model_bakery import baker

from main.models import fEMRUser


def test_edit_organization_when_contact_null():
    u = fEMRUser.objects.create_user(username="test", password="testingpassword", email="logintestinguseremail@email.com")
    u.change_password = False
    Group.objects.get_or_create(name="fEMR Admin")[0].user_set.add(u)
    c = baker.make('main.Campaign')
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    client = Client()
    response = client.post('/login_view/', {'username': 'test', 'password': 'testingpassword'})
    o = baker.make('main.Organization')
    response = client.get('/edit_organization/{0}'.format(o.id))
    assert response.status_code == 200
    assert "contact_edit_form_div" not in str(response.content)
    assert "contact_edit_form_activate" not in str(response.content)
    u.delete()