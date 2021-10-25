from model_bakery import baker

from main.models import Race, Ethnicity, get_nondisclosed_race, get_nondisclosed_ethnicity, State, Organization, \
    get_test_org


def test_get_nondisclosed_race():
    Race.objects.get_or_create(name="Nondisclosed")
    assert isinstance(get_nondisclosed_race(), int)


def test_get_nondisclosed_ethnicity():
    Ethnicity.objects.get_or_create(name="Nondisclosed")
    assert isinstance(get_nondisclosed_ethnicity(), int)


def test_race():
    r = Race.objects.create(name="TestRace")
    assert str(r) == "TestRace"


def test_ethnicity():
    r = Ethnicity.objects.create(name="TestEthnicity")
    assert str(r) == "TestEthnicity"


def test_state():
    s = State.objects.create(name="Test")
    assert str(s) == "Test"


def test_contact():
    s = baker.make('main.Contact')
    assert str(s) == "{0} {1}".format(s.first_name, s.last_name)


def test_get_test_org():
    o = get_test_org()
    org = Organization.objects.get(pk=o)
    assert org.name == "Test"
