from django.shortcuts import redirect, render

from main.models import Campaign, Instance


def organization_admin_home_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="Organization Admin").exists():
            org = Campaign.objects.get(
                name=request.session["campaign"]
            ).instance.organization
            instances = []
            campaigns = []
            try:
                instances = Instance.objects.filter(active=True).filter(
                    admins=request.user
                )
                campaigns = Campaign.objects.filter(active=True).filter(
                    admins=request.user
                )
            except Instance.DoesNotExist:
                pass
            except Campaign.DoesNotExist:
                pass
            return_response = render(
                request,
                "organization_admin/home.html",
                {
                    "user": request.user,
                    "instances": instances,
                    "campaigns": campaigns,
                    "page_name": f"Organization: {org.name}",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
