from django.db.models.query_utils import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Instance


def operation_admin_home(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Operation Admin') | Q(name='Organization Admin')).exists():
            try:
                active_instances = Instance.objects.filter(
                    active=True
                ).filter(
                    admins__in=request.user
                )
            except Instance.DoesNotExist:
                active_instances = list()
            return render(request, 'admin/user_list.html',
                          {'user': request.user,
                           'active_instances': active_instances,
                           'page_name': 'Your Instances'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')