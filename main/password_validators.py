from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from .models import fEMRUser


class NewPasswordValidator(object):
    def validate(self, password, user=None):
        if make_password(password) == user.password:
            raise ValidationError("Password must not match the password currently in use.")

    def get_help_text(self):
        return "Password must not match the password currently in use."