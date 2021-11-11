"""
View functions for administrative actions.
"""
import itertools
import operator
import os
from datetime import datetime, timedelta

from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from axes.utils import reset

from clinic_messages.models import Message
from main.background_tasks import check_admin_permission
from main.femr_admin_views import get_client_ip
from .forms import (
    MOTDForm,
    UserForm,
    UserUpdateForm,
    AdminPasswordForm,
    fEMRAdminUserForm,
    fEMRAdminUserUpdateForm,
)
from .models import MessageOfTheDay, fEMRUser, AuditEntry, DatabaseChangeLog, Campaign


def admin_home(request):
    """
    The landing page for the authenticated administrative user.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the home page.
    """
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            return_response = render(
                request, "admin/home.html", {"user": request.user, "page_name": "Admin"}
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def list_users_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                active_users = Campaign.objects.get(
                    name=request.session["campaign"]
                ).femruser_set.filter(is_active=True)
                inactive_users = Campaign.objects.get(
                    name=request.session["campaign"]
                ).femruser_set.filter(is_active=False)
            except ObjectDoesNotExist:
                active_users = []
                inactive_users = []
            return_response = render(
                request,
                "admin/user_list.html",
                {
                    "user": request.user,
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "page_name": "Clinic Users",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def filter_users_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                data = Campaign.objects.get(
                    name=request.session["campaign"]
                ).femruser_set.filter(is_active=True)
            except ObjectDoesNotExist:
                data = ""
            return_response = render(
                request,
                "admin/user_list.html",
                {"user": request.user, "list_view": data, "page_name": "Clinic Users"},
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def search_users_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                data = Campaign.objects.get(
                    name=request.session["campaign"]
                ).femruser_set.filter(is_active=True)
            except ObjectDoesNotExist:
                data = ""
            return_response = render(
                request,
                "admin/user_list.html",
                {"user": request.user, "list_view": data, "page_name": "Clinic Users"},
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def create_user_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            error = ""
            if request.method == "GET":
                form = (
                    fEMRAdminUserForm()
                    if request.user.groups.filter(name="fEMR Admin").exists()
                    else UserForm()
                )
                return_response = render(
                    request,
                    "admin/user_create_form.html",
                    {"error": error, "form": form},
                )
            if request.method == "POST":
                form = (
                    fEMRAdminUserForm(request.POST)
                    if request.user.groups.filter(name="fEMR Admin").exists()
                    else UserForm(request.POST)
                )
                if form.is_valid():
                    t = form.save()
                    form.save_m2m()
                    t.created_by = request.user
                    t.user_permissions.add(Permission.objects.get(name="Can add state"))
                    t.user_permissions.add(
                        Permission.objects.get(name="Can add diagnosis")
                    )
                    t.user_permissions.add(
                        Permission.objects.get(name="Can add chief complaint")
                    )
                    t.user_permissions.add(
                        Permission.objects.get(name="Can add medication")
                    )
                    t.save()
                    DatabaseChangeLog.objects.create(
                        action="Create",
                        model="User",
                        instance=str(t),
                        ip=get_client_ip(request),
                        username=request.user.username,
                        campaign=Campaign.objects.get(name=request.session["campaign"]),
                    )
                    return_response = render(request, "admin/user_edit_confirmed.html")
                else:
                    return_response = render(
                        request,
                        "admin/user_create_form.html",
                        {"error": "Form is invalid.", "form": form},
                    )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def update_user_view(request, id=None):
    if request.user.is_authenticated:
        error = ""
        m = get_object_or_404(fEMRUser, pk=id)
        if request.method == "POST":
            form = (
                fEMRAdminUserUpdateForm(request.POST or None, instance=m)
                if request.user.groups.filter(name="fEMR Admin").exists()
                else UserUpdateForm(request.user, request.POST or None, instance=m)
            )
            if form.is_valid():
                t = form.save()
                # form.save_m2m()
                t.save()
                DatabaseChangeLog.objects.create(
                    action="Edit",
                    model="User",
                    instance=str(t),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=Campaign.objects.get(name=request.session["campaign"]),
                )
                return_response = render(request, "admin/user_edit_confirmed.html")
            else:
                error = "Form is invalid."
        else:
            form = (
                fEMRAdminUserUpdateForm(instance=m)
                if request.user.groups.filter(name="fEMR Admin").exists()
                else UserUpdateForm(request.user, instance=m)
            )
        return_response = render(
            request,
            "admin/user_edit_form.html",
            {"error": error, "form": form, "user_id": id, "page_name": "Editing User"},
        )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def update_user_password_view(request, id=None):
    if request.user.is_authenticated:
        error = ""
        m = get_object_or_404(fEMRUser, pk=id)
        if request.method == "POST":
            form = AdminPasswordForm(request.POST or None, instance=m)
            if form.is_valid():
                t = form.save()
                t.save()
                m.change_password = True
                m.save()
                DatabaseChangeLog.objects.create(
                    action="Change Password",
                    model="User",
                    instance=str(t),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=Campaign.objects.get(name=request.session["campaign"]),
                )
                return_response = render(request, "admin/user_edit_confirmed.html")
            else:
                error = "Form is invalid."
        else:
            form = AdminPasswordForm(instance=m)
        return_response = render(
            request,
            "admin/user_password_edit_form.html",
            {
                "error": error,
                "form": form,
                "user_id": id,
                "page_name": "Editing User Password",
            },
        )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def lock_user_view(request, id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            m = get_object_or_404(fEMRUser, pk=id)
            m.is_active = False
            m.save()
            return_response = redirect("main:list_users_view")
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def unlock_user_view(request, id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            m = get_object_or_404(fEMRUser, pk=id)
            reset(username=m.username)
            m.is_active = True
            m.save()
            return_response = redirect("main:list_users_view")
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def get_audit_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                data = AuditEntry.objects.filter(
                    Q(campaign=Campaign.objects.get(name=request.session["campaign"]))
                    | Q(action="user_login_failed")
                ).order_by("-timestamp")
            except ObjectDoesNotExist:
                data = ""
            return_response = render(
                request,
                "admin/audit_log_list.html",
                {
                    "user": request.user,
                    "selected": 6,
                    "log": data,
                    "page_name": "Login Log",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def filter_audit_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            selected = 1
            try:
                if request.GET["filter_list"] == "1":
                    now = timezone.make_aware(
                        datetime.today(), timezone.get_default_timezone()
                    )
                    now = now.astimezone(timezone.get_current_timezone())
                    data = (
                        AuditEntry.objects.filter(timestamp__date=now)
                        .order_by("-timestamp")
                        .filter(
                            Q(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            )
                            | Q(action="user_login_failed")
                        )
                    )
                    data = set(
                        list(
                            itertools.chain(
                                data,
                                AuditEntry.objects.filter(timestamp__date=now)
                                .filter(
                                    Q(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    )
                                    | Q(action="user_login_failed")
                                )
                                .order_by("-timestamp"),
                            )
                        )
                    )
                    selected = 1
                elif request.GET["filter_list"] == "2":
                    timestamp_from = timezone.now() - timedelta(days=7)
                    timestamp_to = timezone.now()
                    data = (
                        AuditEntry.objects.filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(
                            Q(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            )
                            | Q(action="user_login_failed")
                        )
                        .order_by("-timestamp")
                    )
                    data = set(
                        list(
                            itertools.chain(
                                data,
                                AuditEntry.objects.filter(
                                    timestamp__gte=timestamp_from,
                                    timestamp__lt=timestamp_to,
                                )
                                .filter(
                                    Q(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    )
                                    | Q(action="user_login_failed")
                                )
                                .order_by("-timestamp"),
                            )
                        )
                    )
                    selected = 2
                elif request.GET["filter_list"] == "3":
                    timestamp_from = timezone.now() - timedelta(days=30)
                    timestamp_to = timezone.now()
                    data = (
                        AuditEntry.objects.filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(
                            Q(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            )
                            | Q(action="user_login_failed")
                        )
                        .order_by("-timestamp")
                    )
                    data = set(
                        list(
                            itertools.chain(
                                data,
                                AuditEntry.objects.filter(
                                    timestamp__gte=timestamp_from,
                                    timestamp__lt=timestamp_to,
                                )
                                .filter(
                                    Q(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    )
                                    | Q(action="user_login_failed")
                                )
                                .order_by("-timestamp"),
                            )
                        )
                    )
                    selected = 3
                elif request.GET["filter_list"] == "4":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d"
                        ).replace(hour=0, minute=0, second=0, microsecond=0)
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d"
                        ).replace(hour=23, minute=59, second=59, microsecond=0)
                        data = (
                            AuditEntry.objects.filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                Q(
                                    campaign=Campaign.objects.get(
                                        name=request.session["campaign"]
                                    )
                                )
                                | Q(action="user_login_failed")
                            )
                            .order_by("-timestamp")
                        )
                        data = set(
                            list(
                                itertools.chain(
                                    data,
                                    AuditEntry.objects.filter(
                                        timestamp__gte=timestamp_from,
                                        timestamp__lt=timestamp_to,
                                    )
                                    .filter(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    )
                                    .order_by("-timestamp"),
                                )
                            )
                        )
                    except ValueError:
                        data = []
                    selected = 4
                elif request.GET["filter_list"] == "5":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_start"], "%Y-%m-%d"
                        )
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_end"], "%Y-%m-%d"
                        ) + timedelta(days=1)
                        data = (
                            AuditEntry.objects.filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                Q(
                                    campaign=Campaign.objects.get(
                                        name=request.session["campaign"]
                                    )
                                )
                                | Q(action="user_login_failed")
                            )
                            .order_by("-timestamp")
                        )
                        data = set(
                            list(
                                itertools.chain(
                                    data,
                                    AuditEntry.objects.filter(
                                        timestamp__gte=timestamp_from,
                                        timestamp__lt=timestamp_to,
                                    )
                                    .filter(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    )
                                    .order_by("-timestamp"),
                                )
                            )
                        )
                    except ValueError:
                        data = []
                    selected = 5
                elif request.GET["filter_list"] == "6":
                    try:
                        data = AuditEntry.objects.filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        ).order_by("-timestamp")
                    except ValueError:
                        data = []
                    selected = 6
                else:
                    data = []
            except ObjectDoesNotExist:
                data = []
            data = sorted(data, key=operator.attrgetter("timestamp"), reverse=True)
            return_response = render(
                request,
                "admin/audit_log_list.html",
                {
                    "user": request.user,
                    "selected": selected,
                    "log": data,
                    "page_name": "Login Log",
                    "filter_day": request.GET["date_filter_day"],
                    "filter_start": request.GET["date_filter_start"],
                    "filter_end": request.GET["date_filter_end"],
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def search_audit_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                data = AuditEntry.objects.filter(
                    Q(campaign=Campaign.objects.get(name=request.session["campaign"]))
                    | Q(action="user_login_failed")
                )
            except ObjectDoesNotExist:
                data = ""
            return_response = render(
                request,
                "admin/audit_log_list.html",
                {"user": request.user, "list_view": data, "page_name": "Login Log"},
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def export_audit_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            return_response = render(
                request,
                "export/audit_logfile.html",
                {
                    "log": AuditEntry.objects.filter(
                        campaign=Campaign.objects.get(name=request.session["campaign"])
                    )
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def get_database_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                excludemodels = ["Campaign", "Instance"]
                data = (
                    DatabaseChangeLog.objects.exclude(model__in=excludemodels)
                    .filter(
                        campaign=Campaign.objects.get(name=request.session["campaign"])
                    )
                    .order_by("-timestamp")
                )
            except ObjectDoesNotExist:
                data = []
            return_response = render(
                request,
                "admin/database_log_list.html",
                {
                    "user": request.user,
                    "selected": 6,
                    "list_view": data,
                    "page_name": "Patient Change Log",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def filter_database_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            selected = 1
            excludemodels = ["Campaign", "Instance"]
            try:
                if request.GET["filter_list"] == "1":
                    now = timezone.make_aware(
                        datetime.today(), timezone.get_default_timezone()
                    )
                    now = now.astimezone(timezone.get_current_timezone())
                    data = (
                        DatabaseChangeLog.objects.exclude(model__in=excludemodels)
                        .filter(timestamp__date=now)
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        )
                    )
                    data = set(
                        list(
                            itertools.chain(
                                data,
                                DatabaseChangeLog.objects.exclude(
                                    model__in=excludemodels
                                )
                                .filter(timestamp__date=now)
                                .filter(
                                    campaign=Campaign.objects.get(
                                        name=request.session["campaign"]
                                    )
                                ),
                            )
                        )
                    )
                    selected = 1
                elif request.GET["filter_list"] == "2":
                    timestamp_from = timezone.now() - timedelta(days=7)
                    timestamp_to = timezone.now()
                    data = (
                        DatabaseChangeLog.objects.exclude(model__in=excludemodels)
                        .filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        )
                    )
                    data = set(
                        list(
                            itertools.chain(
                                data,
                                DatabaseChangeLog.objects.exclude(
                                    model__in=excludemodels
                                )
                                .filter(
                                    timestamp__gte=timestamp_from,
                                    timestamp__lt=timestamp_to,
                                )
                                .filter(
                                    campaign=Campaign.objects.get(
                                        name=request.session["campaign"]
                                    )
                                ),
                            )
                        )
                    )
                    selected = 2
                elif request.GET["filter_list"] == "3":
                    timestamp_from = timezone.now() - timedelta(days=30)
                    timestamp_to = timezone.now()
                    data = (
                        DatabaseChangeLog.objects.exclude(model__in=excludemodels)
                        .filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        )
                    )
                    data = set(
                        list(
                            itertools.chain(
                                data,
                                DatabaseChangeLog.objects.exclude(
                                    model__in=excludemodels
                                )
                                .filter(
                                    timestamp__gte=timestamp_from,
                                    timestamp__lt=timestamp_to,
                                )
                                .filter(
                                    campaign=Campaign.objects.get(
                                        name=request.session["campaign"]
                                    )
                                ),
                            )
                        )
                    )
                    selected = 3
                elif request.GET["filter_list"] == "4":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d"
                        ).replace(hour=0, minute=0, second=0, microsecond=0)
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d"
                        ).replace(hour=23, minute=59, second=59, microsecond=0)
                        data = (
                            DatabaseChangeLog.objects.exclude(model__in=excludemodels)
                            .filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            )
                        )
                        data = set(
                            list(
                                itertools.chain(
                                    data,
                                    DatabaseChangeLog.objects.exclude(
                                        model__in=excludemodels
                                    )
                                    .filter(
                                        timestamp__gte=timestamp_from,
                                        timestamp__lt=timestamp_to,
                                    )
                                    .filter(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    ),
                                )
                            )
                        )
                    except ValueError:
                        data = []
                    selected = 4
                elif request.GET["filter_list"] == "5":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_start"], "%Y-%m-%d"
                        )
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_end"], "%Y-%m-%d"
                        ) + timedelta(days=1)
                        data = (
                            DatabaseChangeLog.objects.exclude(model__in=excludemodels)
                            .filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            )
                        )
                        data = set(
                            list(
                                itertools.chain(
                                    data,
                                    DatabaseChangeLog.objects.exclude(
                                        model__in=excludemodels
                                    )
                                    .filter(
                                        timestamp__gte=timestamp_from,
                                        timestamp__lt=timestamp_to,
                                    )
                                    .filter(
                                        campaign=Campaign.objects.get(
                                            name=request.session["campaign"]
                                        )
                                    ),
                                )
                            )
                        )
                    except ValueError:
                        data = []
                    selected = 5
                elif request.GET["filter_list"] == "6":
                    try:
                        data = DatabaseChangeLog.objects.exclude(
                            model__in=excludemodels
                        ).filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        )
                    except ValueError:
                        data = []
                    selected = 6
                else:
                    data = []
            except ObjectDoesNotExist:
                data = []
            data = sorted(data, key=operator.attrgetter("timestamp"), reverse=True)
            return_response = render(
                request,
                "admin/database_log_list.html",
                {
                    "user": request.user,
                    "selected": selected,
                    "list_view": data,
                    "page_name": "Patient Change Log",
                    "filter_day": request.GET["date_filter_day"],
                    "filter_start": request.GET["date_filter_start"],
                    "filter_end": request.GET["date_filter_end"],
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def search_database_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            try:
                excludemodels = ["Campaign", "Instance"]
                data = DatabaseChangeLog.objects.exclude(
                    model__in=excludemodels
                ).filter(
                    campaign=Campaign.objects.get(name=request.session["campaign"])
                )
            except ObjectDoesNotExist:
                data = ""
            return_response = render(
                request,
                "admin/database_log_list.html",
                {
                    "user": request.user,
                    "list_view": data,
                    "page_name": "Patient Change Log",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def export_database_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            excludemodels = ["Campaign", "Instance"]
            return_response = render(
                request,
                "export/data_logfile.html",
                {
                    "log": DatabaseChangeLog.objects.exclude(
                        model__in=excludemodels
                    ).filter(
                        campaign=Campaign.objects.get(name=request.session["campaign"])
                    )
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def add_users_to_campaign(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            return_response = render(
                request,
                "admin/add_users_to_campaign.html",
                {"users": __retrieve_needed_users(request)},
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def add_user_to_campaign(request, user_id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            user = fEMRUser.objects.get(pk=user_id)
            user.campaigns.add(Campaign.objects.get(name=request.session["campaign"]))
            user.save()
            return_response = render(
                request,
                "admin/add_users_to_campaign.html",
                {"users": __retrieve_needed_users(request)},
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def cut_user_from_campaign(request, user_id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            user = fEMRUser.objects.get(pk=user_id)
            user.campaigns.remove(
                Campaign.objects.get(name=request.session["campaign"])
            )
            user.save()
            return_response = render(
                request,
                "admin/add_users_to_campaign.html",
                {"users": __retrieve_needed_users(request)},
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def __retrieve_needed_users(request):
    users_created_by_me = fEMRUser.objects.filter(created_by=request.user)
    users_in_my_campaigns = fEMRUser.objects.filter(
        campaigns__in=request.user.campaigns.all()
    ).filter(is_active=True)
    users = set(list(itertools.chain(users_created_by_me, users_in_my_campaigns)))
    return users


def message_of_the_day_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            m = MessageOfTheDay.load()
            form = MOTDForm()
            if request.method == "GET":
                form = MOTDForm(instance=m)
                form.initial["text"] = m.text
                form.initial["start_date"] = m.start_date
                form.initial["end_date"] = m.end_date
            elif request.method == "POST":
                form = MOTDForm(request.POST, instance=m)
                if form.is_valid():
                    m.text = request.POST["text"]
                    m.start_date = request.POST["start_date"]
                    m.end_date = request.POST["end_date"]
                    m.save()
                    for u in fEMRUser.objects.all():
                        Message.objects.create(
                            sender=request.user,
                            recipient=u,
                            subject="fEMR On-Chain",
                            content=m.text,
                        )
                        if os.environ.get("EMAIL_HOST") != "":
                            send_mail(
                                "fEMR On-Chain",
                                "f{m.text}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. "
                                "PLEASE DO NOT REPLY TO "
                                "THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.",
                                os.environ.get("DEFAULT_FROM_EMAIL"),
                                [u.email],
                            )
            return_response = render(
                request, "admin/motd.html", {"form": form, "page_name": "MotD"}
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
