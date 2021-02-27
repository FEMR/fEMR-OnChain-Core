"""
View functions for top-level locations.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from main.forms import ForgotUsernameForm
from django.core.exceptions import ObjectDoesNotExist
from main.models import Campaign, fEMRUser
from django.http import HttpResponse
from django.shortcuts import render, redirect
import pytz


def index(request):
    """
    Initial landing view.

    :param request: A Django request object.
    :return: A template rendered as an HTTPResponse.
    """
    print(request.user_agent.browser.family)
    if request.user_agent.browser.family != "Chrome" and request.user_agent.browser.family != "Firefox":
        return render(request, 'data/stop.html')
    else:
        return redirect('main:login_view')


def home(request):
    """
    The landing page for the authenticated administrative user.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the home page.
    """
    if request.user.is_authenticated:
        return render(request, 'data/home.html', {'user': request.user,
                                                  'page_name': 'Home',
                                                  'campaigns': request.user.campaigns.filter(active=True),
                                                  'selected_campaign': request.session['campaign']})
    else:
        return redirect('main:not_logged_in')


def library(request):
    """
    The root of the main library page, where clinical users of the application can view
    and manage the data models contained in the fEMR On-Chain database.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the library page.
    """
    if request.user.is_authenticated:
        return render(request, 'data/library.html', {'user': request.user})
    else:
        return redirect('main:not_logged_in')


def healthcheck(request):
    """
    Returns a success message.
    """
    return HttpResponse()


def set_timezone(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            if request.method == 'POST':
                request.session['django_timezone'] = request.POST['timezone']
                campaign = Campaign.objects.get(name=request.session['campaign'])
                campaign.timezone = request.POST['timezone']
                campaign.save()
                return redirect('main:index')
            else:
                return render(request, 'data/timezone.html', {'timezones': pytz.common_timezones})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def forgot_username(request):
    if request.method == 'POST':
        try:
            user = fEMRUser.objects.get(email__iexact=request.POST['email'])
            from django.core.mail import send_mail
            send_mail(
                'Username Recovery',
                'Someone recently requested a username reminder from fEMR On-Chain. If this was you, your username is {}. If it wasn\'t you, you can safely ignore this email.'.format(
                    user.username),
                'noreply@teamfemr.org',
                [user.email]
            )
        except ObjectDoesNotExist:
            print("Email not sending - {}.".format(request.POST['email']))
        return render(request, 'data/username_sent.html')
    else:
        form = ForgotUsernameForm()
        return render(request, 'data/forgot_username.html', {'form': form})


def help_messages_off(request):
    if request.user.is_authenticated:
        request.session['tags_off'] = None if request.session.get('tags_off', None) else True
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('main:not_logged_in')
