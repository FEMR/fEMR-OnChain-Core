from django.shortcuts import redirect
from django.db.models.query_utils import Q

from main.background_tasks import check_admin_permission


def is_authenticated(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return_response = view_func(request, *args, **kwargs)
        else:
            return_response = redirect("main:not_logged_in")
        return return_response

    return wrap


def is_femr_admin(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name="fEMR Admin").exists():
            return_response = view_func(request, *args, **kwargs)
        else:
            return_response = redirect("main:permission_denied")
        return return_response

    return wrap


def is_org_admin(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name="Organization Admin").exists():
            return_response = view_func(request, *args, **kwargs)
        else:
            return_response = redirect("main:permission_denied")
        return return_response

    return wrap


def is_op_admin(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(
            Q(name="Operation Admin") | Q(name="Organization Admin")
        ).exists():
            return_response = view_func(request, *args, **kwargs)
        else:
            return_response = redirect("main:permission_denied")
        return return_response

    return wrap


def is_admin(view_func):
    def wrap(request, *args, **kwargs):
        if check_admin_permission(request.user):
            return_response = view_func(request, *args, **kwargs)
        else:
            return_response = redirect("main:permission_denied")
        return return_response

    return wrap


def in_recovery_mode(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.current_campaign == "RECOVERY MODE":
            return_response = redirect("main:home")
        else:
            return_response = view_func(request, *args, **kwargs)
        return return_response

    return wrap
