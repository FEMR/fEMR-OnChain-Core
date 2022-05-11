from django.contrib.auth.models import Group
from django.test.client import Client
from model_bakery import baker

from main.models import fEMRUser


def test_formulary_home_view():
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
    return_response = client.get("/formulary_home_view/")
    assert return_response.status_code == 200
    u.delete()
    c.delete()


def test_edit_supply_view():
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
    item = baker.make("main.InventoryEntry")
    return_response = client.get("/edit_supply/{0}".format(item.id))
    assert return_response.status_code == 200
    u.delete()
    c.delete()


def test_post_edit_supply_view():
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
    item = baker.make("main.InventoryEntry")
    category = baker.make("main.InventoryCategory")
    medication = baker.make("main.Medication")
    form = baker.make("main.InventoryForm")
    manufacturer = baker.make("main.Manufacturer")
    return_response = client.post(
        "/edit_supply/{0}".format(item.id),
        {
            "amount": "1",
            "box_number": "1233",
            "category": category.id,
            "count": "1",
            "count_unit": "cm",
            "expiration_date": "2022-05-31",
            "form": form.id,
            "initial_quantity": "4",
            "item_number": "32412",
            "manufacturer": manufacturer.id,
            "medication": medication.id,
            "quantity": "1",
            "quantity_unit": "duck",
            "strength": "1",
            "strength_unit": "lulz",
        },
    )
    assert return_response.status_code == 200
    u.delete()
    c.delete()
