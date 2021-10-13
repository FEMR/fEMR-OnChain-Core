from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError


class NewPasswordValidator(object):
    @staticmethod
    def validate(password, user=None):
        if check_password(password, user.password):
            raise ValidationError("Password must not match the password currently in use.")

    @staticmethod
    def get_help_text():
        return "Password must not match the password currently in use."
