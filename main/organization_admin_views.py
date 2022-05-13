from django.shortcuts import render
from main.decorators import is_authenticated, is_org_admin

from main.models import Campaign, Instance


@is_org_admin
@is_authenticated
def organization_admin_home_view(request):
    org = Campaign.objects.get(name=request.user.current_campaign).instance.organization
    instances = []
    campaigns = []
    try:
        instances = Instance.objects.filter(active=True).filter(admins=request.user)
        campaigns = Campaign.objects.filter(active=True).filter(admins=request.user)
    except Instance.DoesNotExist:
        pass
    except Campaign.DoesNotExist:
        pass
    return render(
        request,
        "organization_admin/home.html",
        {
            "user": request.user,
            "instances": instances,
            "campaigns": campaigns,
            "page_name": f"Organization: {org.name}",
        },
    )
