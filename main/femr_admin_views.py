from django.shortcuts import get_object_or_404, redirect, render
from silk.profiling.profiler import silk_profile
from main.decorators import is_authenticated, is_femr_admin

from main.forms import (
    CampaignForm,
    EthnicityForm,
    InstanceForm,
    OrganizationForm,
    RaceForm,
    fEMRAdminUserForm,
    fEMRAdminUserUpdateForm,
)
from main.models import (
    AuditEntry,
    Campaign,
    DatabaseChangeLog,
    Instance,
    Organization,
    fEMRUser,
)


@is_authenticated
def femr_admin_home(request):
    if request.method == "POST":
        return_response = redirect("main:index")
    else:
        return_response = render(
            request, "femr_admin/home.html", {"page_name": "fEMR Admin"}
        )
    return return_response


@is_authenticated
def change_campaign(request):
    if request.method == "POST":
        campaign = request.POST.get("campaign", None)
        if campaign is not None:
            request.user.current_campaign = campaign
            request.user.save()
            AuditEntry.objects.create(
                action="user_changed_campaigns",
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
                browser_user_agent=request.user_agent.browser.family,
                system_user_agent=request.user_agent.os.family,
            )
        return_response = redirect("main:home")
    else:
        return_response = redirect("main:index")
    return return_response


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(",")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")
    return ip_address


@is_femr_admin
@is_authenticated
def new_campaign_view(request):
    campaign_name = request.session.get("campaign", None)
    if campaign_name == "RECOVERY MODE":
        return_value = render(request, "femr_admin/campaign/op_not_permitted.html")
    else:
        if request.method == "POST":
            form = CampaignForm(request.POST)
            if form.is_valid():
                item = form.save()
                item.save()
                DatabaseChangeLog.objects.create(
                    action="Create",
                    model="Campaign",
                    instance=str(item),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=Campaign.objects.get(name=request.user.current_campaign),
                )
                return_value = render(
                    request, "femr_admin/confirm/campaign_submitted.html"
                )
            else:
                return_value = render(
                    request,
                    "femr_admin/campaign/new_campaign.html",
                    {"form": form, "page_name": "New Campaign"},
                )
        else:
            form = CampaignForm()
            return_value = render(
                request,
                "femr_admin/campaign/new_campaign.html",
                {"form": form, "page_name": "New Campaign"},
            )
    return return_value


@is_femr_admin
@is_authenticated
def new_instance_view(request):
    if request.method == "POST":
        form = InstanceForm(request.POST)
        contact_form = fEMRAdminUserForm()
        if form.is_valid():
            item = form.save()
            item.save()
            DatabaseChangeLog.objects.create(
                action="Create",
                model="Instance",
                instance=str(item),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
            )
            return_value = render(request, "femr_admin/confirm/instance_submitted.html")
        else:
            return_value = render(
                request,
                "femr_admin/instance/new_instance.html",
                {
                    "form": form,
                    "contact_form": contact_form,
                    "page_name": "New Operation",
                    "show": False,
                },
            )
    else:
        return_value = render(
            request,
            "femr_admin/instance/new_instance.html",
            {
                "form": InstanceForm(),
                "contact_form": fEMRAdminUserForm(),
                "page_name": "New Operation",
                "show": False,
            },
        )
    return return_value


@is_femr_admin
@is_authenticated
def new_contact_view(request):
    form = InstanceForm()
    contact_form = fEMRAdminUserForm()
    if request.method == "POST":
        contact_form = fEMRAdminUserForm(request.POST)
        if contact_form.is_valid():
            item = contact_form.save()
            item.campaigns.add(Campaign.objects.get(name="Test"))
            item.save()
            DatabaseChangeLog.objects.create(
                action="Create",
                model="Contact",
                instance=str(item),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
            )
            contact_form = fEMRAdminUserForm()
    return render(
        request,
        "femr_admin/instance/new_instance.html",
        {
            "form": form,
            "contact_form": contact_form,
            "page_name": "New Operation",
            "show": True,
        },
    )


@is_femr_admin
@is_authenticated
def edit_campaign_view(request, campaign_id=None):
    campaign_name = request.session.get("campaign", None)
    if campaign_name == "RECOVERY MODE":
        return_response = render(request, "femr_admin/campaign/op_not_permitted.html")
    else:
        instance = Campaign.objects.get(pk=campaign_id)
        if request.method == "POST":
            form = CampaignForm(request.POST or None, instance=instance)
            if form.is_valid():
                item = form.save()
                item.save()
                DatabaseChangeLog.objects.create(
                    action="Edit",
                    model="Campaign",
                    instance=str(item),
                    ip=get_client_ip(request),
                    username=request.user.username,
                    campaign=instance,
                )
                return_response = render(
                    request, "femr_admin/confirm/campaign_submitted.html"
                )
            else:
                return_response = render(
                    request,
                    "femr_admin/campaign/edit_campaign.html",
                    {
                        "form": form,
                        "page_name": "Edit Campaign",
                        "campaign_id": campaign_id,
                    },
                )
        else:
            form = CampaignForm(instance=instance)
            return_response = render(
                request,
                "femr_admin/campaign/edit_campaign.html",
                {
                    "form": form,
                    "page_name": "Edit Campaign",
                    "campaign_id": campaign_id,
                },
            )
    return return_response


@is_femr_admin
@is_authenticated
def edit_contact_view(request, user_id=None):
    instance = fEMRUser.objects.get(pk=user_id)
    if request.method == "POST":
        form = fEMRAdminUserUpdateForm(request.POST or None, instance=instance)
        if form.is_valid():
            item = form.save()
            item.save()
            DatabaseChangeLog.objects.create(
                action="Edit",
                model="Contact",
                instance=str(item),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
            )
            return_value = render(request, "femr_admin/confirm/contact_submitted.html")
        else:
            return_value = render(
                request,
                "femr_admin/contact/edit_contact.html",
                {
                    "form": form,
                    "page_name": "Edit Contact",
                    "contact_id": user_id,
                },
            )
    else:
        return_value = render(
            request,
            "femr_admin/contact/edit_contact.html",
            {
                "form": fEMRAdminUserUpdateForm(instance=instance),
                "page_name": "Edit Contact",
                "contact_id": user_id,
            },
        )
    return return_value


@is_femr_admin
@is_authenticated
def view_contact_view(request, user_id=None):
    instance = fEMRUser.objects.get(pk=user_id)
    return render(
        request,
        "femr_admin/contact/contact_info.html",
        {"instance": instance, "page_name": "Contact Info"},
    )


@is_femr_admin
@is_authenticated
def edit_instance_view(request, instance_id=None):
    instance = Instance.objects.get(pk=instance_id)
    contact = instance.main_contact
    contact_form = fEMRAdminUserForm()
    edit_contact_form = fEMRAdminUserUpdateForm(instance=contact)
    if request.method == "POST":
        form = InstanceForm(request.POST or None, instance=instance)
        if form.is_valid():
            item = form.save()
            item.save()
            DatabaseChangeLog.objects.create(
                action="Edit",
                model="Instance",
                instance=str(item),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
            )
            return_response = render(
                request, "femr_admin/confirm/instance_submitted.html"
            )
    else:
        form = InstanceForm(instance=instance)
        return_response = render(
            request,
            "femr_admin/instance/edit_instance.html",
            {
                "form": form,
                "contact_form": contact_form,
                "edit_contact_form": edit_contact_form,
                "page_name": "Edit Instance",
                "contact_id": contact.id,
                "instance_id": instance_id,
            },
        )
    return return_response


@is_femr_admin
@is_authenticated
def list_campaign_view(request):
    active_campaigns = Campaign.objects.filter(active=True).order_by(
        "instance__name", "name"
    )
    inactive_campaigns = Campaign.objects.filter(active=False).order_by(
        "instance__name", "name"
    )
    return render(
        request,
        "femr_admin/campaign/list_campaign.html",
        {
            "active_campaigns": active_campaigns,
            "inactive_campaigns": inactive_campaigns,
            "page_name": "Campaigns",
        },
    )


@is_femr_admin
@is_authenticated
def list_instance_view(request):
    active_instances = Instance.objects.filter(active=True).order_by("name")
    inactive_instances = Instance.objects.filter(active=False).order_by("name")
    return render(
        request,
        "femr_admin/instance/list_instance.html",
        {
            "active_instances": active_instances,
            "inactive_instances": inactive_instances,
            "page_name": "Operations",
        },
    )


@is_femr_admin
@is_authenticated
def lock_instance_view(_, instance_id=None):
    instance = get_object_or_404(Instance, pk=instance_id)
    instance.active = False
    instance.save()
    for campaign in instance.campaign_set.all().iterator():
        campaign.active = False
        campaign.save()
    return redirect("main:list_instance")


@is_femr_admin
@is_authenticated
def unlock_instance_view(_, instance_id=None):
    instance = get_object_or_404(Instance, pk=instance_id)
    instance.active = True
    instance.save()
    return redirect("main:list_instance")


@is_femr_admin
@is_authenticated
def lock_campaign_view(_, campaign_id=None):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    campaign.active = False
    campaign.save()
    return redirect("main:list_campaign")


@is_femr_admin
@is_authenticated
def unlock_campaign_view(_, campaign_id=None):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    campaign.active = True
    campaign.instance.active = True
    campaign.instance.save()
    campaign.save()
    return redirect("main:list_campaign")


@is_femr_admin
@is_authenticated
def new_race_view(request):
    if request.method == "POST":
        form = RaceForm(request.POST)
        if form.is_valid():
            item = form.save()
            item.save()
            return_response = redirect(request.META.get("HTTP_REFERER"))
        else:
            return_response = render(
                request, "femr_admin/race/new_race.html", {"form": form}
            )
    else:
        form = RaceForm()
        return_response = render(
            request, "femr_admin/race/new_race.html", {"form": form}
        )
    return return_response


@is_femr_admin
@is_authenticated
def new_ethnicity_view(request):
    if request.method == "POST":
        form = EthnicityForm(request.POST)
        if form.is_valid():
            item = form.save()
            item.save()
            return_response = redirect(request.META.get("HTTP_REFERER"))
        else:
            return_response = render(
                request, "femr_admin/race/new_ethnicity.html", {"form": form}
            )
    else:
        form = EthnicityForm()
        return_response = render(
            request, "femr_admin/race/new_ethnicity.html", {"form": form}
        )
    return return_response


@is_femr_admin
@is_authenticated
def list_organization_view(request):
    organizations = Organization.objects.all().iterator()
    return render(
        request,
        "femr_admin/organization/list_organization.html",
        {
            "user": request.user,
            "organizations": organizations,
            "page_name": "Organizations",
        },
    )


@is_femr_admin
@is_authenticated
@silk_profile("edit-organization-view")
def edit_organization_view(request, organization_id=None):
    instance = Organization.objects.get(pk=organization_id)
    contact = instance.main_contact
    contact_form = fEMRAdminUserForm()
    edit_contact_form = fEMRAdminUserUpdateForm(instance=contact)
    if request.method == "POST":
        form = OrganizationForm(request.POST or None, instance=instance)
        if form.is_valid():
            item = form.save()
            item.save()
            DatabaseChangeLog.objects.create(
                action="Edit",
                model="Organization",
                instance=str(item),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
            )
            return_response = render(
                request, "femr_admin/confirm/organization_submitted.html"
            )
    else:
        form = OrganizationForm(instance=instance)
        return_response = render(
            request,
            "femr_admin/organization/edit_organization.html",
            {
                "form": form,
                "contact_form": contact_form,
                "edit_contact_form": edit_contact_form,
                "page_name": "Edit Organization",
                "contact_id": contact.id if contact is not None else None,
                "instance_id": organization_id,
            },
        )
    return return_response


@is_femr_admin
@is_authenticated
def new_organization_view(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        contact_form = fEMRAdminUserForm()
        if form.is_valid():
            item = form.save()
            item.save()
            DatabaseChangeLog.objects.create(
                action="Create",
                model="Organization",
                instance=str(item),
                ip=get_client_ip(request),
                username=request.user.username,
                campaign=Campaign.objects.get(name=request.user.current_campaign),
            )
            return_response = render(
                request, "femr_admin/confirm/organization_submitted.html"
            )
        else:
            return_response = render(
                request,
                "femr_admin/organization/new_organization.html",
                {
                    "form": form,
                    "contact_form": contact_form,
                    "page_name": "New Organization",
                    "show": False,
                },
            )
    else:
        form = OrganizationForm()
        contact_form = fEMRAdminUserForm()
        return_response = render(
            request,
            "femr_admin/organization/new_organization.html",
            {
                "form": form,
                "contact_form": contact_form,
                "page_name": "New Organization",
                "show": False,
            },
        )
    return return_response
