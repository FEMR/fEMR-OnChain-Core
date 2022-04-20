from django.shortcuts import redirect, render

from main.models import Campaign


def femr_admin_dashboard_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="fEMR Admin").exists():
            campaigns = Campaign.objects.filter(active=True).order_by('id')
            return_response = render(
                request,
                "dashboard/femr_admin.html",
                {
                    "campaigns": campaigns,
                    "page_name": "Metrics",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response