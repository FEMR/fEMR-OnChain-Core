from django.shortcuts import render

from main.decorators import is_authenticated, is_op_admin

from .models import Instance


@is_op_admin
@is_authenticated
def operation_admin_home_view(request):
    try:
        active_instances = Instance.objects.filter(active=True).filter(
            admins=request.user
        )
    except Instance.DoesNotExist:
        active_instances = []
    return render(
        request,
        "operation_admin/home.html",
        {
            "user": request.user,
            "active_instances": active_instances,
            "page_name": "Your Operations",
        },
    )
