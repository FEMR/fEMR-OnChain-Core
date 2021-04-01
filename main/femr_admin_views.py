from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import CampaignForm, ContactForm, InstanceForm
from main.models import AuditEntry, Campaign, Contact, DatabaseChangeLog, Instance
from django.db.models import ObjectDoesNotExist


def femr_admin_home(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            return redirect('main:index')
        else:
            return render(request, 'femr_admin/home.html')
    else:
        return redirect('main:not_logged_in')


def change_campaign(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            campaign = request.POST.get('campaign', None)
            if campaign is not None:
                request.session['campaign'] = campaign
                AuditEntry.objects.create(action='user_changed_campaigns',
                                            ip=get_client_ip(request),
                                            username=request.user.username,
                                            campaign=Campaign.objects.get(name=request.session['campaign']))
            else:
                campaign = "RECOVERY MODE"
            return redirect('main:home')
        else:
            return redirect('main:index')
    else:
        return redirect('main:not_logged_in')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def new_campaign_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            campaign_name = request.session.get('campaign', None)
            if campaign_name == "RECOVERY MODE":
                return render(request, 'femr_admin/campaign/op_not_permitted.html')
            else:
                if request.method == 'POST':
                    form = CampaignForm(request.POST)
                    if form.is_valid():
                        t = form.save()
                        t.save()
                        DatabaseChangeLog.objects.create(action="Create", model="Campaign", instance=str(t),
                                                        ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                        return render(request, "femr_admin/confirm/campaign_submitted.html")
                    else:
                        return render(request, 'femr_admin/campaign/new_campaign.html', {'form': form, 'page_name': 'New Campaign'})
                else:
                    form = CampaignForm()
                    return render(request, 'femr_admin/campaign/new_campaign.html', {'form': form, 'page_name': 'New Campaign'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def new_instance_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            if request.method == 'POST':
                form = InstanceForm(request.POST)
                contact_form = ContactForm()
                if form.is_valid():
                    t = form.save()
                    t.save()
                    DatabaseChangeLog.objects.create(action="Create", model="Instance", instance=str(t),
                                                     ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                    return render(request, "femr_admin/confirm/instance_submitted.html")
            else:
                form = InstanceForm()
                contact_form = ContactForm()
            return render(request, 'femr_admin/instance/new_instance.html', {'form': form, 'contact_form': contact_form, 'page_name': 'New Instance', 'show': False})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def new_contact_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            form = InstanceForm()
            contact_form = ContactForm()
            if request.method == 'POST':
                contact_form = ContactForm(request.POST)
                if contact_form.is_valid():
                    t = contact_form.save()
                    t.save()
                    DatabaseChangeLog.objects.create(action="Create", model="Contact", instance=str(t),
                                                     ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                    contact_form = ContactForm()
            return render(request, 'femr_admin/instance/new_instance.html', {'form': form, 'contact_form': contact_form, 'page_name': 'New Instance', 'show': True})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def edit_campaign_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            campaign_name = request.session.get('campaign', None)
            if campaign_name == "RECOVERY MODE":
                return render(request, 'femr_admin/campaign/op_not_permitted.html')
            else:
                instance = Campaign.objects.get(pk=id)
                if request.method == 'POST':
                    form = CampaignForm(request.POST or None, instance=instance)
                    if form.is_valid():
                        t = form.save()
                        t.save()
                        DatabaseChangeLog.objects.create(action="Edit", model="Campaign", instance=str(t),
                                                        ip=get_client_ip(request), username=request.user.username, campaign=instance)
                        return render(request, "femr_admin/confirm/campaign_submitted.html")
                else:
                    form = CampaignForm(instance=instance)
                    return render(request, 'femr_admin/campaign/edit_campaign.html', {'form': form, 'page_name': 'Edit Campaign', 'campaign_id': id})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def edit_contact_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            instance = Contact.objects.get(pk=id)
            if request.method == 'POST':
                form = ContactForm(request.POST or None, instance=instance)
                if form.is_valid():
                    t = form.save()
                    t.save()
                    DatabaseChangeLog.objects.create(action="Edit", model="Contact", instance=str(t),
                                                     ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                    return render(request, "femr_admin/confirm/contact_submitted.html")
            else:
                form = ContactForm(instance=instance)
                return render(request, 'femr_admin/contact/edit_contact.html', {'form': form, 'page_name': 'Edit Contact', 'contact_id': id})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def view_contact_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            instance = Contact.objects.get(pk=id)
            return render(request, 'femr_admin/contact/contact_info.html', {'instance': instance, 'page_name': 'Contact Info'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def edit_instance_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            instance = Instance.objects.get(pk=id)
            contact_form = ContactForm()
            if request.method == 'POST':
                form = InstanceForm(request.POST or None, instance=instance)
                if form.is_valid():
                    t = form.save()
                    t.save()
                    DatabaseChangeLog.objects.create(action="Edit", model="Instance", instance=str(t),
                                                     ip=get_client_ip(request), username=request.user.username, campaign=Campaign.objects.get(name=request.session['campaign']))
                    return render(request, "femr_admin/confirm/instance_submitted.html")
            else:
                form = InstanceForm(instance=instance)
                return render(request, 'femr_admin/instance/edit_instance.html', {'form': form, 'contact_form': contact_form, 'page_name': 'Edit Instance', 'instance_id': id})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def list_campaign_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            active_campaigns = Campaign.objects.filter(active=True).order_by('instance__name', 'name')
            inactive_campaigns = Campaign.objects.filter(active=False).order_by('instance__name', 'name')
            return render(request, 'femr_admin/campaign/list_campaign.html', {'active_campaigns': active_campaigns,
                                                                              'inactive_campaigns': inactive_campaigns,
                                                                              'page_name': 'Campaigns'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def list_instance_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='fEMR Admin').exists():
            active_instances = Instance.objects.filter(active=True).order_by('name')
            inactive_instances = Instance.objects.filter(active=False).order_by('name')
            return render(request, 'femr_admin/instance/list_instance.html', {'active_instances': active_instances,
                                                                              'inactive_instances': inactive_instances,
                                                                              'page_name': 'Instances'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def lock_instance_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            m = get_object_or_404(Instance, pk=id)
            m.active = False
            m.save()
            for c in m.campaign_set.all():
                c.active = False
                c.save()
            return redirect('main:list_instance')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def unlock_instance_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            m = get_object_or_404(Instance, pk=id)
            m.active = True
            m.save()
            return redirect('main:list_instance')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def lock_campaign_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            m = get_object_or_404(Campaign, pk=id)
            m.active = False
            m.save()
            return redirect('main:list_campaign')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def unlock_campaign_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            m = get_object_or_404(Campaign, pk=id)
            m.active = True
            m.save()
            return redirect('main:list_campaign')
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def problem_delete_view(request):
    if request.user.is_authenticated:
        data = Instance.objects.all()
        try:
            p = get_object_or_404(Instance, pk=id)
            Instance.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return redirect('main:list_instance')
    else:
        return redirect('main:not_logged_in')
