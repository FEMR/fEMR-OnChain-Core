from django.core.exceptions import ValidationError

from main.models import fEMRUser
from main.password_validators import NewPasswordValidator


def test_new_password_validator_no_match():
    u = fEMRUser.objects.create_user(username="testuser", password="testpassword", email="test@test.com")
    v = NewPasswordValidator()
    v.validate("newpassword", u)


def test_new_password_validator_match():
    u = fEMRUser.objects.create_user(username="testuserraises", password="testpassword", email="another@test.com")
    v = NewPasswordValidator()
    try:
        v.validate("testpassword", u)
        raise AssertionError("An exception was not raised.")
    except ValidationError:
        assert True


def test_new_password_validator():
    v = NewPasswordValidator()
    assert v.get_help_text() == "Password must not match the password currently in use."
