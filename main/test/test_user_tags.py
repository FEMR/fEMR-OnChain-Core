from model_bakery import baker

from main.models import fEMRUser
from main.templatetags.user_tags import campaign_active, has_campaign


def test_has_campaign():
    u = fEMRUser.objects.create_user(
        username="testhomeagain",
        password="testingpassword",
        email="hometestinguseremail@email.com",
    )
    u.change_password = False
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    u.campaigns.add(c)
    u.save()
    has_campaign(u, c.name)
    u.delete()
    c.delete()


def test_campaign_active():
    c = baker.make("main.Campaign")
    c.active = True
    c.save()
    assert campaign_active(c.name)
    c.delete()
    d = baker.make("main.Campaign")
    d.active = True
    d.save()
    assert campaign_active(d.name)
    d.delete()
