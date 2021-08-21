from django.shortcuts import redirect, render
from main.models import Campaign, Instance


def organization_admin_home_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Organization Admin').exists():
            try:
                instances = Instance.objects.filter(
                    active=True
                ).filter(
                    admins__in=request.user
                )
                campaigns = Campaign.objects.filter(
                    active=True
                ).filter(
                    admins__in=request.user
                )
            except Instance.DoesNotExist:
                instances = list()
            except Campaign.DoesNotExist:
                campaigns = list()
            return render(request, 'organization_admin/home.html',
                          {'user': request.user,
                           'instances': instances,
                           'campaigns': campaigns,
                           'page_name': 'Clinic Users'})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')