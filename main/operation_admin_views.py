from django.db.models.query_utils import Q
from django.shortcuts import render, redirect

from .models import Instance


def operation_admin_home_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(
            Q(name="Operation Admin") | Q(name="Organization Admin")
        ).exists():
            try:
                active_instances = Instance.objects.filter(active=True).filter(
                    admins=request.user
                )
            except Instance.DoesNotExist:
                active_instances = []
            return_response = render(
                request,
                "operation_admin/home.html",
                {
                    "user": request.user,
                    "active_instances": active_instances,
                    "page_name": "Your Operations",
                },
            )
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
