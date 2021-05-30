from clinic_messages.models import Message
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from django.http import request
from main.forms import LoginForm
from django.shortcuts import render
from main.models import Campaign
import pytz

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not AnonymousUser:
            if 'campaign' not in request.session or request.session['campaign'] == "RECOVERY MODE":
                try:
                    request.session['campaign'] = request.user.campaigns.filter(active=True)[
                        0].name
                    tzname = Campaign.objects.get(
                        name=request.session['campaign']).timezone
                except IndexError:
                    if request.user.groups.filter(name='fEMR Admin').exists():
                        request.session['campaign'] = "RECOVERY MODE"
                    tzname = request.session.get('django_timezone')
            else:
                tzname = Campaign.objects.get(
                    name=request.session['campaign']).timezone
        else:
            tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)


class CampaignActivityCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_admin = request.user.groups.filter(name='fEMR Admin').exists()
        if request.user.is_authenticated and not is_admin:
            campaign_name = request.session.get('campaign', None)
            if campaign_name is None:
                print("Campaign is NONE for {}".format(request.user.username))
                try:
                    request.session['campaign'] = request.user.campaigns.filter(active=True)[
                        0].name
                    return self.get_response(request)
                except:
                    logout(request)
                    form = LoginForm()
                    return render(request, 'auth/login.html',
                                  {
                                      'form': form,
                                      'error_message': 'You have no active campaigns. Please contact your administrator to proceed.'
                                  })
            campaign = Campaign.objects.get(name=campaign_name)
            if not campaign.active:
                print("Campaign is inactive for {}".format(request.user.username))
                del request.session['campaign']
                logout(request)
                form = LoginForm()
                return render(request, 'auth/login.html',
                              {
                                  'form': form,
                                  'error_message': 'Your active campaign has been deactivated. Please log in again to proceed.'
                              })
            else:
                return self.get_response(request)
        elif request.user.is_authenticated and is_admin:
            campaign_name = request.session.get('campaign', None)
            if campaign_name is None:
                if len(request.user.campaigns.filter(active=True)) != 0:
                    request.session['campaign'] = request.user.campaigns.filter(active=True)[
                        0].name
                else:
                    request.session['campaign'] = "RECOVERY MODE"
                return self.get_response(request)
            elif campaign_name != "RECOVERY MODE":
                campaign = Campaign.objects.get(
                    name=request.session['campaign'])
                if not campaign.active:
                    if len(request.user.campaigns.filter(active=True)) != 0:
                        request.session['campaign'] = request.user.campaigns.filter(active=True)[
                            0].name
                    else:
                        request.session['campaign'] = "RECOVERY MODE"
                    return self.get_response(request)
                else:
                    return self.get_response(request)
            else:
                return self.get_response(request)
        else:
            return self.get_response(request)


class ClinicMessageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.message_number = len(Message.objects.filter(recipient=request.user))
        return self.get_response(request)
