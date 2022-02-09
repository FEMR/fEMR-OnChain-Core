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
from main.forms import (
    MOTDForm,
    UserForm,
    UserUpdateForm,
    AdminPasswordForm,
    fEMRAdminUserForm,
    fEMRAdminUserUpdateForm,
)
from main.models import (
    MessageOfTheDay,
    fEMRUser,
    AuditEntry,
    DatabaseChangeLog,
    Campaign,
)


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


def __create_user_view_get(request):
    form = (
        fEMRAdminUserForm()
        if request.user.groups.filter(name="fEMR Admin").exists()
        else UserForm()
    )
    return render(
        request,
        "admin/user_create_form.html",
        {"error": "", "form": form},
    )


def __create_user_view_post(request):
    form = (
        fEMRAdminUserForm(request.POST)
        if request.user.groups.filter(name="fEMR Admin").exists()
        else UserForm(request.POST)
    )
    if form.is_valid():
        item = form.save()
        form.save_m2m()
        item.created_by = request.user
        item.user_permissions.add(Permission.objects.get(name="Can add state"))
        item.user_permissions.add(Permission.objects.get(name="Can add diagnosis"))
        item.user_permissions.add(
            Permission.objects.get(name="Can add chief complaint")
        )
        item.user_permissions.add(Permission.objects.get(name="Can add medication"))
        item.save()
        DatabaseChangeLog.objects.create(
            action="Create",
            model="User",
            instance=str(item),
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
    return return_response


def create_user_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            if request.method == "GET":
                return_response = __create_user_view_get(request)
            if request.method == "POST":
                return_response = __create_user_view_post(request)
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def update_user_view(request, user_id=None):
    if request.user.is_authenticated:
        error = ""
        user = get_object_or_404(fEMRUser, pk=user_id)
        if request.method == "POST":
            form = (
                fEMRAdminUserUpdateForm(request.POST or None, instance=user)
                if request.user.groups.filter(name="fEMR Admin").exists()
                else UserUpdateForm(request.user, request.POST or None, instance=user)
            )
            if form.is_valid():
                item = form.save()
                item.save()
                DatabaseChangeLog.objects.create(
                    action="Edit",
                    model="User",
                    instance=str(item),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=Campaign.objects.get(name=request.session["campaign"]),
                )
                return_response = render(request, "admin/user_edit_confirmed.html")
            else:
                return_response = render(
                    request,
                    "admin/user_edit_form.html",
                    {
                        "error": "Form is invalid.",
                        "form": form,
                        "user_id": user_id,
                        "page_name": "Editing User",
                    },
                )
        else:
            form = (
                fEMRAdminUserUpdateForm(instance=user)
                if request.user.groups.filter(name="fEMR Admin").exists()
                else UserUpdateForm(request.user, instance=user)
            )
            return_response = render(
                request,
                "admin/user_edit_form.html",
                {
                    "error": error,
                    "form": form,
                    "user_id": user_id,
                    "page_name": "Editing User",
                },
            )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def update_user_password_view(request, user_id=None):
    if request.user.is_authenticated:
        error = ""
        user = get_object_or_404(fEMRUser, pk=user_id)
        if request.method == "POST":
            form = AdminPasswordForm(request.POST or None, instance=user)
            if form.is_valid():
                item = form.save()
                item.save()
                user.change_password = True
                user.save()
                DatabaseChangeLog.objects.create(
                    action="Change Password",
                    model="User",
                    instance=str(item),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=Campaign.objects.get(name=request.session["campaign"]),
                )
                return_response = render(request, "admin/user_edit_confirmed.html")
            else:
                error = "Form is invalid."
        else:
            form = AdminPasswordForm(instance=user)
        return_response = render(
            request,
            "admin/user_password_edit_form.html",
            {
                "error": error,
                "form": form,
                "user_id": user_id,
                "page_name": "Editing User Password",
            },
        )
    else:
        return_response = redirect("/not_logged_in")
    return return_response


def lock_user_view(request, user_id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            user = get_object_or_404(fEMRUser, pk=user_id)
            user.is_active = False
            user.save()
            return_response = redirect("main:list_users_view")
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response


def unlock_user_view(request, user_id=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            user = get_object_or_404(fEMRUser, pk=user_id)
            reset(username=user.username)
            user.is_active = True
            user.last_login = timezone.now()
            user.save()
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


def __filter_audit_logs_process(request):
    try:
        logs = AuditEntry.objects.all()
        campaign = Campaign.objects.get(name=request.session["campaign"])
        if request.GET["filter_list"] == "1":
            now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
            now = now.astimezone(timezone.get_current_timezone())
            data = set(
                list(
                    itertools.chain(
                        logs.filter(timestamp__date=now)
                        .order_by("-timestamp")
                        .filter(Q(campaign=campaign) | Q(action="user_login_failed")),
                        logs.filter(timestamp__date=now)
                        .filter(Q(campaign=campaign) | Q(action="user_login_failed"))
                        .order_by("-timestamp"),
                    )
                )
            )
            selected = 1
        elif request.GET["filter_list"] == "2":
            timestamp_from = timezone.now() - timedelta(days=7)
            timestamp_to = timezone.now()
            data = set(
                list(
                    itertools.chain(
                        logs.filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(Q(campaign=campaign) | Q(action="user_login_failed"))
                        .order_by("-timestamp"),
                        logs.filter(
                            timestamp__gte=timestamp_from,
                            timestamp__lt=timestamp_to,
                        )
                        .filter(Q(campaign=campaign) | Q(action="user_login_failed"))
                        .order_by("-timestamp"),
                    )
                )
            )
            selected = 2
        elif request.GET["filter_list"] == "3":
            timestamp_from = timezone.now() - timedelta(days=30)
            timestamp_to = timezone.now()
            data = set(
                list(
                    itertools.chain(
                        logs.filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(Q(campaign=campaign) | Q(action="user_login_failed"))
                        .order_by("-timestamp"),
                        logs.filter(
                            timestamp__gte=timestamp_from,
                            timestamp__lt=timestamp_to,
                        )
                        .filter(Q(campaign=campaign) | Q(action="user_login_failed"))
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
                data = set(
                    list(
                        itertools.chain(
                            logs.filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                Q(campaign=campaign) | Q(action="user_login_failed")
                            )
                            .order_by("-timestamp"),
                            logs.filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(campaign=campaign)
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
                data = set(
                    list(
                        itertools.chain(
                            logs.filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                Q(campaign=campaign) | Q(action="user_login_failed")
                            )
                            .order_by("-timestamp"),
                            logs.filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(campaign=campaign)
                            .order_by("-timestamp"),
                        )
                    )
                )
            except ValueError:
                data = []
            selected = 5
        elif request.GET["filter_list"] == "6":
            try:
                data = logs.filter(campaign=campaign).order_by("-timestamp")
            except ValueError:
                data = []
            selected = 6
        else:
            data = []
    except ObjectDoesNotExist:
        data = []
    data = sorted(data, key=operator.attrgetter("timestamp"), reverse=True)
    return render(
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


def filter_audit_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            return_response = __filter_audit_logs_process(request)
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


def __filter_database_logs_check(request):
    excludemodels = ["Campaign", "Instance"]
    try:
        logs = DatabaseChangeLog.objects.all()
        if request.GET["filter_list"] == "1":
            now = timezone.make_aware(datetime.today(), timezone.get_default_timezone())
            now = now.astimezone(timezone.get_current_timezone())
            data = set(
                list(
                    itertools.chain(
                        logs.exclude(model__in=excludemodels)
                        .filter(timestamp__date=now)
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        ),
                        logs.exclude(model__in=excludemodels)
                        .filter(timestamp__date=now)
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        ),
                    )
                )
            )
        elif request.GET["filter_list"] == "2":
            timestamp_from = timezone.now() - timedelta(days=7)
            timestamp_to = timezone.now()
            data = set(
                list(
                    itertools.chain(
                        logs.exclude(model__in=excludemodels)
                        .filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        ),
                        logs.exclude(model__in=excludemodels)
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
        elif request.GET["filter_list"] == "3":
            timestamp_from = timezone.now() - timedelta(days=30)
            timestamp_to = timezone.now()
            data = set(
                list(
                    itertools.chain(
                        logs.exclude(model__in=excludemodels)
                        .filter(
                            timestamp__gte=timestamp_from, timestamp__lt=timestamp_to
                        )
                        .filter(
                            campaign=Campaign.objects.get(
                                name=request.session["campaign"]
                            )
                        ),
                        logs.exclude(model__in=excludemodels)
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
        elif request.GET["filter_list"] == "4":
            try:
                timestamp_from = datetime.strptime(
                    request.GET["date_filter_day"], "%Y-%m-%d"
                ).replace(hour=0, minute=0, second=0, microsecond=0)
                timestamp_to = datetime.strptime(
                    request.GET["date_filter_day"], "%Y-%m-%d"
                ).replace(hour=23, minute=59, second=59, microsecond=0)
                data = set(
                    list(
                        itertools.chain(
                            logs.exclude(model__in=excludemodels)
                            .filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            ),
                            logs.exclude(model__in=excludemodels)
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
        elif request.GET["filter_list"] == "5":
            try:
                timestamp_from = datetime.strptime(
                    request.GET["date_filter_start"], "%Y-%m-%d"
                )
                timestamp_to = datetime.strptime(
                    request.GET["date_filter_end"], "%Y-%m-%d"
                ) + timedelta(days=1)
                data = set(
                    list(
                        itertools.chain(
                            logs.exclude(model__in=excludemodels)
                            .filter(
                                timestamp__gte=timestamp_from,
                                timestamp__lt=timestamp_to,
                            )
                            .filter(
                                campaign=Campaign.objects.get(
                                    name=request.session["campaign"]
                                )
                            ),
                            logs.exclude(model__in=excludemodels)
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
        elif request.GET["filter_list"] == "6":
            try:
                data = logs.exclude(model__in=excludemodels).filter(
                    campaign=Campaign.objects.get(name=request.session["campaign"])
                )
            except ValueError:
                data = []
        else:
            data = []
    except ObjectDoesNotExist:
        data = []
    data = sorted(data, key=operator.attrgetter("timestamp"), reverse=True)
    return render(
        request,
        "admin/database_log_list.html",
        {
            "user": request.user,
            "selected": int(request.GET["filter_list"]),
            "list_view": data,
            "page_name": "Patient Change Log",
            "filter_day": request.GET["date_filter_day"],
            "filter_start": request.GET["date_filter_start"],
            "filter_end": request.GET["date_filter_end"],
        },
    )


def filter_database_logs_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            return_response = __filter_database_logs_check(request)
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
    user_set = fEMRUser.objects.all()
    users_created_by_me = user_set.filter(created_by=request.user)
    users_in_my_campaigns = user_set.filter(
        campaigns__in=request.user.campaigns.all()
    ).filter(is_active=True)
    users = set(list(itertools.chain(users_created_by_me, users_in_my_campaigns)))
    return users


def __message_of_the_day_form_processor(request, message):
    form = MOTDForm(request.POST, instance=message)
    if form.is_valid():
        message.text = request.POST["text"]
        message.start_date = request.POST["start_date"]
        message.end_date = request.POST["end_date"]
        message.save()
        for user in fEMRUser.objects.filter(is_active=True):
            Message.objects.create(
                sender=request.user,
                recipient=user,
                subject="fEMR On-Chain",
                content=message.text,
            )
            if os.environ.get("EMAIL_HOST") != "":
                send_mail(
                    "fEMR On-Chain",
                    f"{message.text}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN."
                    "PLEASE DO NOT REPLY TO "
                    "THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.",
                    os.environ.get("DEFAULT_FROM_EMAIL"),
                    [user.email],
                )
        return_response = render(request, "admin/motd_confirm.html")
    else:
        return_response = render(
            request, "admin/motd.html", {"form": form, "page_name": "MotD"}
        )
    return return_response


def message_of_the_day_view(request):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            message = MessageOfTheDay.load()
            form = MOTDForm()
            if request.method == "GET":
                form = MOTDForm(instance=message)
                form.initial["text"] = message.text
                form.initial["start_date"] = message.start_date
                form.initial["end_date"] = message.end_date
                return_response = render(
                    request, "admin/motd.html", {"form": form, "page_name": "MotD"}
                )
            elif request.method == "POST":
                return_response = __message_of_the_day_form_processor(request, message)
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
