from django.shortcuts import render
from main.decorators import is_authenticated, is_femr_admin

from main.models import Campaign


@is_femr_admin
@is_authenticated
def femr_admin_dashboard_view(request):
    campaigns = Campaign.objects.filter(active=True).order_by("id")
    return render(
        request,
        "dashboard/femr_admin.html",
        {
            "campaigns": campaigns,
            "page_name": "Metrics",
        },
    )
