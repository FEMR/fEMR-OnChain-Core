from django.shortcuts import render
from main.decorators import is_authenticated, is_femr_admin

from main.models import AuditEntry, Campaign


def user_agent_list():
    browsers = {}
    logs = AuditEntry.objects.all()
    for log in logs:
        if log.browser_user_agent is not None:
            if log.browser_user_agent in browsers:
                browsers[log.browser_user_agent] += 1
            else:
                browsers[log.browser_user_agent] = 1
        if log.system_user_agent is not None:
            if log.system_user_agent in browsers:
                browsers[log.system_user_agent] += 1
            else:
                browsers[log.system_user_agent] = 1
    return browsers


@is_femr_admin
@is_authenticated
def femr_admin_dashboard_view(request):
    campaigns = Campaign.objects.filter(active=True).order_by("id")
    browsers = user_agent_list()
    return render(
        request,
        "dashboard/femr_admin.html",
        {
            "campaigns": campaigns,
            "browsers": browsers,
            "page_name": "Metrics",
        },
    )
