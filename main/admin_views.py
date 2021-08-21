"""
View functions for administrative actions.
"""
import os

from django.db.models.query_utils import Q
from clinic_messages.models import Message
from datetime import datetime, timedelta
import itertools
import operator

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .forms import MOTDForm, UserForm, UserUpdateForm, AdminPasswordForm, fEMRAdminUserForm, fEMRAdminUserUpdateForm
from .models import Instance, MessageOfTheDay, fEMRUser, AuditEntry, DatabaseChangeLog, Campaign


def admin_home(request):
    """
    The landing page for the authenticated administrative user.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the home page.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            return render(request, 'admin/home.html', {'user': request.user, 'page_name': 'Admin'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


# -------------------------------------------------------------------------------------------------------
# User control views
# -------------------------------------------------------------------------------------------------------
def list_users_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                active_users = Campaign.objects.get(
                    name=request.session['campaign']).femruser_set.filter(is_active=True)
                inactive_users = Campaign.objects.get(
                    name=request.session['campaign']).femruser_set.filter(is_active=False)
            except ObjectDoesNotExist:
                active_users = list()
                inactive_users = list()
            return render(request, 'admin/user_list.html',
                          {'user': request.user,
                           'active_users': active_users,
                           'inactive_users': inactive_users,
                           'page_name': 'Clinic Users'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def filter_users_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                data = Campaign.objects.get(
                    name=request.session['campaign']).femruser_set.filter(is_active=True)
            except ObjectDoesNotExist:
                data = ""
            return render(request, 'admin/user_list.html',
                          {'user': request.user,
                           'list_view': data, 'page_name': 'Clinic Users'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def search_users_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                data = Campaign.objects.get(
                    name=request.session['campaign']).femruser_set.filter(is_active=True)
            except ObjectDoesNotExist:
                data = ""
            return render(request, 'admin/user_list.html',
                          {'user': request.user,
                           'list_view': data, 'page_name': 'Clinic Users'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def create_user_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            error = ""
            if request.method == "GET":
                form = fEMRAdminUserForm() if request.user.groups.filter(
                    name='fEMR Admin').exists() else UserForm()
                return render(request, 'admin/user_create_form.html', {'error': error, 'form': form})
            if request.method == "POST":
                form = fEMRAdminUserForm(request.POST) if request.user.groups.filter(
                    name='fEMR Admin').exists() else UserForm(request.POST)
                if form.is_valid():
                    t = form.save()
                    if request.user.groups.filter(name='fEMR Admin').exists():
                        for x in request.POST.getlist('campaigns'):
                            t.campaigns.add(Campaign.objects.get(pk=(int(x))))
                    if request.user.groups.filter(name='fEMR Admin').exists():
                        for x in request.POST.getlist('groups'):
                            t.groups.add(x)
                    t.created_by = request.user
                    t.save()
                    DatabaseChangeLog.objects.create(action="Create", model="User", instance=str(t),
                                                     ip=request.META.get('REMOTE_ADDR'), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                    return render(request, "admin/user_edit_confirmed.html")
                else:
                    error = "Form is invalid."
                return render(request, 'admin/user_create_form.html', {'error': error,
                                                                       'form': form})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def update_user_view(request, id=None):
    if request.user.is_authenticated:
        error = ""
        m = get_object_or_404(fEMRUser, pk=id)
        if request.method == 'POST':
            form = fEMRAdminUserUpdateForm(request.POST or None,
                                           instance=m) if request.user.groups.filter(
                name='fEMR Admin').exists() else UserUpdateForm(request.user, request.POST or None,
                                                                instance=m)
            if form.is_valid():
                t = form.save()
                t.save()
                DatabaseChangeLog.objects.create(action="Edit", model="User", instance=str(t),
                                                 ip=request.META.get('REMOTE_ADDR'), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                return render(request, "admin/user_edit_confirmed.html")
            else:
                error = "Form is invalid."
        else:
            form = fEMRAdminUserUpdateForm(instance=m) if request.user.groups.filter(
                name='fEMR Admin').exists() else UserUpdateForm(request.user, instance=m)
        return render(request, 'admin/user_edit_form.html', {'error': error,
                                                             'form': form,
                                                             'user_id': id,
                                                             'page_name': 'Editing User'})
    else:
        return redirect('/not_logged_in')


def update_user_password_view(request, id=None):
    if request.user.is_authenticated:
        error = ""
        m = get_object_or_404(fEMRUser, pk=id)
        if request.method == 'POST':
            form = AdminPasswordForm(request.POST or None,
                                     instance=m)
            if form.is_valid():
                t = form.save()
                t.save()
                m.change_password = True
                m.save()
                DatabaseChangeLog.objects.create(action="Change Password", model="User", instance=str(t),
                                                 ip=request.META.get('REMOTE_ADDR'), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                form = AdminPasswordForm()
                error = "Form submitted successfully."
                return render(request, "admin/user_edit_confirmed.html")
            else:
                error = "Form is invalid."
        else:
            form = AdminPasswordForm(instance=m)
        return render(request, 'admin/user_password_edit_form.html', {'error': error,
                                                                      'form': form,
                                                                      'user_id': id,
                                                                      'page_name': 'Editing User Password'})
    else:
        return redirect('/not_logged_in')


def lock_user_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            m = get_object_or_404(fEMRUser, pk=id)
            m.is_active = False
            m.save()
            return redirect('main:list_users_view')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def unlock_user_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            m = get_object_or_404(fEMRUser, pk=id)
            m.is_active = True
            m.save()
            return redirect('main:list_users_view')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


# -------------------------------------------------------------------------------------------------------
# Audit Log Control Views
# -------------------------------------------------------------------------------------------------------
def get_audit_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                data = AuditEntry.objects.filter(campaign=Campaign.objects.get(
                    name=request.session['campaign'])).order_by('-timestamp')
            except ObjectDoesNotExist:
                data = ""
            return render(request, 'admin/audit_log_list.html',
                          {'user': request.user, 'selected': 6,
                           'log': data, 'page_name': 'Login Log'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def filter_audit_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            selected = 1
            try:
                if request.GET["filter_list"] == "1":
                    now = timezone.make_aware(
                        datetime.today(), timezone.get_default_timezone())
                    now = now.astimezone(timezone.get_current_timezone())
                    data = AuditEntry.objects.filter(
                        timestamp__date=now).order_by('-timestamp').filter(campaign=Campaign.objects.get(name=request.session['campaign']))
                    data = set(list(itertools.chain(
                        data, AuditEntry.objects.filter(timestamp__date=now).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp'))))
                    selected = 1
                elif request.GET["filter_list"] == "2":
                    timestamp_from = timezone.now() - timedelta(days=7)
                    timestamp_to = timezone.now()
                    data = AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                     timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp')
                    data = set(list(itertools.chain(data, AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                                                    timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp'))))
                    selected = 2
                elif request.GET["filter_list"] == "3":
                    timestamp_from = timezone.now() - timedelta(days=30)
                    timestamp_to = timezone.now()
                    data = AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                     timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp')
                    data = set(list(itertools.chain(data, AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                                                    timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp'))))
                    selected = 3
                elif request.GET["filter_list"] == "4":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=0)
                        data = AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                         timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp')
                        data = set(list(itertools.chain(data, AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                                                        timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp'))))
                    except ValueError:
                        data = list()
                    selected = 4
                elif request.GET["filter_list"] == "5":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_start"], "%Y-%m-%d")
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_end"], "%Y-%m-%d") + timedelta(days=1)
                        data = AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                         timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp')
                        data = set(list(itertools.chain(data, AuditEntry.objects.filter(timestamp__gte=timestamp_from,
                                                                                        timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp'))))
                    except ValueError:
                        data = list()
                    selected = 5
                elif request.GET["filter_list"] == "6":
                    try:
                        data = AuditEntry.objects.filter(campaign=Campaign.objects.get(
                            name=request.session['campaign'])).order_by('-timestamp')
                    except ValueError:
                        data = list()
                    selected = 6
                else:
                    data = list()
            except ObjectDoesNotExist:
                data = list()
            data = sorted(data, key=operator.attrgetter(
                'timestamp'), reverse=True)
            return render(request, 'admin/audit_log_list.html',
                          {'user': request.user, 'selected': selected,
                           'log': data, 'page_name': 'Login Log',
                           'filter_day': request.GET["date_filter_day"],
                           'filter_start': request.GET["date_filter_start"],
                           'filter_end': request.GET["date_filter_end"]})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def search_audit_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                data = AuditEntry.objects.filter(
                    campaign=Campaign.objects.get(name=request.session['campaign']))
            except ObjectDoesNotExist:
                data = ""
            return render(request, 'admin/audit_log_list.html',
                          {'user': request.user,
                           'list_view': data, 'page_name': 'Login Log'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def export_audit_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            return render(request, 'export/audit_logfile.html', {'log': AuditEntry.objects.filter(campaign=Campaign.objects.get(name=request.session['campaign']))})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


# -------------------------------------------------------------------------------------------------------
# Database Log Control Views
# -------------------------------------------------------------------------------------------------------
def get_database_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                excludemodels = ['Campaign', 'Instance']
                data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(
                    campaign=Campaign.objects.get(name=request.session['campaign'])).order_by('-timestamp')
            except ObjectDoesNotExist:
                data = list()
            return render(request, 'admin/database_log_list.html',
                          {'user': request.user, 'selected': 6,
                           'list_view': data, 'page_name': 'Patient Change Log'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def filter_database_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            selected = 1
            excludemodels = ['Campaign', 'Instance']
            try:
                if request.GET["filter_list"] == "1":
                    now = timezone.make_aware(
                        datetime.today(), timezone.get_default_timezone())
                    now = now.astimezone(timezone.get_current_timezone())
                    data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(
                        timestamp__date=now).filter(campaign=Campaign.objects.get(name=request.session['campaign']))
                    data = set(list(itertools.chain(
                        data, DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__date=now).filter(campaign=Campaign.objects.get(name=request.session['campaign'])))))
                    selected = 1
                elif request.GET["filter_list"] == "2":
                    timestamp_from = timezone.now() - timedelta(days=7)
                    timestamp_to = timezone.now()
                    data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                             timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign']))
                    data = set(list(itertools.chain(data, DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                                                            timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])))))
                    selected = 2
                elif request.GET["filter_list"] == "3":
                    timestamp_from = timezone.now() - timedelta(days=30)
                    timestamp_to = timezone.now()
                    data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                             timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign']))
                    data = set(list(itertools.chain(data, DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                                                            timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])))))
                    selected = 3
                elif request.GET["filter_list"] == "4":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_day"], "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=0)
                        data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                                 timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign']))
                        data = set(list(itertools.chain(data, DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                                                                timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])))))
                    except ValueError:
                        data = list()
                    selected = 4
                elif request.GET["filter_list"] == "5":
                    try:
                        timestamp_from = datetime.strptime(
                            request.GET["date_filter_start"], "%Y-%m-%d")
                        timestamp_to = datetime.strptime(
                            request.GET["date_filter_end"], "%Y-%m-%d") + timedelta(days=1)
                        data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                                 timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign']))
                        data = set(list(itertools.chain(data, DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(timestamp__gte=timestamp_from,
                                                                                                                                timestamp__lt=timestamp_to).filter(campaign=Campaign.objects.get(name=request.session['campaign'])))))
                    except ValueError:
                        data = list()
                    selected = 5
                elif request.GET["filter_list"] == "6":
                    try:
                        data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(
                            campaign=Campaign.objects.get(name=request.session['campaign']))
                    except ValueError:
                        data = list()
                    selected = 6
                else:
                    data = list()
            except ObjectDoesNotExist:
                data = list()
            data = sorted(data, key=operator.attrgetter(
                'timestamp'), reverse=True)
            return render(request, 'admin/database_log_list.html',
                          {'user': request.user, 'selected': selected,
                           'list_view': data, 'page_name': 'Patient Change Log',
                           'filter_day': request.GET["date_filter_day"],
                           'filter_start': request.GET["date_filter_start"],
                           'filter_end': request.GET["date_filter_end"]})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def search_database_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            try:
                excludemodels = ['Campaign', 'Instance']
                data = DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(
                    campaign=Campaign.objects.get(name=request.session['campaign']))
            except ObjectDoesNotExist:
                data = ""
            return render(request, 'admin/database_log_list.html',
                          {'user': request.user,
                           'list_view': data, 'page_name': 'Patient Change Log'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def export_database_logs_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            excludemodels = ['Campaign', 'Instance']
            return render(request, 'export/data_logfile.html', {'log': DatabaseChangeLog.objects.exclude(model__in=excludemodels).filter(campaign=Campaign.objects.get(name=request.session['campaign']))})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def add_users_to_campaign(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            return render(request, 'admin/add_users_to_campaign.html', {'users': __retrieve_needed_users(request)})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def add_user_to_campaign(request, user_id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            user = fEMRUser.objects.get(pk=user_id)
            user.campaigns.add(Campaign.objects.get(
                name=request.session['campaign']))
            user.save()
            return render(request, 'admin/add_users_to_campaign.html', {'users': __retrieve_needed_users(request)})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def cut_user_from_campaign(request, user_id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            user = fEMRUser.objects.get(pk=user_id)
            user.campaigns.remove(Campaign.objects.get(
                name=request.session['campaign']))
            user.save()
            return render(request, 'admin/add_users_to_campaign.html', {'users': __retrieve_needed_users(request)})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def __retrieve_needed_users(request):
    users_created_by_me = fEMRUser.objects.filter(created_by=request.user)
    users_in_my_campaigns = fEMRUser.objects.filter(
        campaigns__in=request.user.campaigns.all()).filter(is_active=True)
    users = set(list(itertools.chain(
        users_created_by_me, users_in_my_campaigns)))
    return users


def message_of_the_day_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') | Q(name='Organization Admin') | Q(name='Operation Admin')).exists():
            print("Loading form.")
            m = MessageOfTheDay.load()
            if request.method == "GET":
                print("GET")
                form = MOTDForm(instance=m)
                form.initial['text'] = m.text
                form.initial['start_date'] = m.start_date
                form.initial['end_date'] = m.end_date
            elif request.method == "POST":
                print("Post fires.")
                form = MOTDForm(request.POST, instance=m)
                if form.is_valid():
                    print("Form is valid.")
                    m.text = request.POST['text']
                    m.start_date = request.POST['start_date']
                    m.end_date = request.POST['end_date']
                    m.save()
                    for u in fEMRUser.objects.all():
                        Message.objects.create(
                            sender=request.user,
                            recipient=u,
                            subject="fEMR On-Chain",
                            content=m.text
                        )
                        if os.environ.get('EMAIL_HOST') != "":
                            send_mail(
                                "fEMR On-Chain",
                                "{0}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.".format(
                                    m.text),
                                os.environ.get('DEFAULT_FROM_EMAIL'),
                                [u.email])
                else:
                    print(form.is_valid())
                    print(form.errors)
            print(form.initial)
            return render(request, 'admin/motd.html', {'form': form, 'page_name': "MotD"})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')
