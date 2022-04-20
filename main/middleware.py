"""
Middleware classes intended to intercept requests and enact logic before they hit a view.
"""
import pytz
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.utils import timezone

from clinic_messages.models import Message
from main.forms import LoginForm
from main.models import Campaign, UserSession, fEMRUser


class TimezoneMiddleware:
    """
    A Middleware class to handle setting the current timezone to the current campaign's
    selected timezone. This will also handle initially setting the current session's
    campaign if it hasn't been set yet.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not AnonymousUser:
            if request.user.current_campaign == "RECOVERY MODE":
                try:
                    request.user.current_campaign = request.user.campaigns.filter(
                        active=True
                    )[0].name
                    request.user.save()
                    tzname = Campaign.objects.get(
                        name=request.user.current_campaign
                    ).timezone
                except IndexError:
                    if request.user.groups.filter(name="fEMR Admin").exists():
                        request.user.current_campaign = "RECOVERY MODE"
                        request.user.save()
                    tzname = request.session.get("django_timezone")
            else:
                tzname = Campaign.objects.get(
                    name=request.user.current_campaign
                ).timezone
        else:
            tzname = request.session.get("django_timezone")
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)


class CampaignActivityCheckMiddleware:
    """
    Defines middleware to stop non-admin users from logging in if their campaigns are all inactive.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_admin = request.user.groups.filter(name="fEMR Admin").exists()
        if request.user.is_authenticated:
            self.__check_valid_campaign(request.user)
            if not is_admin:
                return_response = self.__user_not_admin(request)
            else:
                return_response = self.__run_if_admin(request, is_admin)
        else:
            return_response = self.get_response(request)
        return return_response

    @staticmethod
    def __check_valid_campaign(user):
        campaigns = user.campaigns.filter(active=True)
        if user.current_campaign != "RECOVERY_MODE":
            try:
                campaigns.get(name=user.current_campaign)
            except Campaign.DoesNotExist:
                if len(campaigns) != 0:
                    user.current_campaign = campaigns[0].name
                    user.save()

    def __user_not_admin(self, request):
        campaign_name = request.user.current_campaign
        if campaign_name is None or campaign_name == "":
            return_response = self.__campaign_is_none(request)
            campaign = None
        else:
            return_response = self.get_response(request)
            campaign = Campaign.objects.get(name=campaign_name)
        if campaign and not campaign.active:
            return_response = self.__campaign_not_active(request)
        return return_response

    @staticmethod
    def __campaign_not_active(request):
        logout(request)
        form = LoginForm()
        return render(
            request,
            "auth/login.html",
            {
                "form": form,
                "error_message": "Your active campaign has been deactivated. "
                "Please log in again to proceed.",
            },
        )

    def __campaign_is_none(self, request):
        campaigns = request.user.campaigns.filter(active=True)
        if len(campaigns) != 0:
            request.user.current_campaign = campaigns[0].name
            request.user.save()
            return_response = self.get_response(request)
        else:
            logout(request)
            return_response = render(
                request,
                "auth/login.html",
                {
                    "form": LoginForm(),
                    "error_message": "You have no active campaigns. Please contact your "
                    "administrator to proceed. ",
                },
            )
        return return_response

    def __run_if_admin(self, request, is_admin):
        if request.user.is_authenticated and is_admin:
            campaign_name = request.user.current_campaign
            if campaign_name is None or campaign_name == "":
                return_response = self.__campaign_name_is_none(request)
            elif campaign_name != "RECOVERY MODE":
                return_response = self.__campaign_not_in_recovery_mode(request)
            else:
                return_response = self.get_response(request)
        else:
            return_response = self.get_response(request)
        return return_response

    def __campaign_name_is_none(self, request):
        if len(request.user.campaigns.filter(active=True)) != 0:
            request.user.current_campaign = request.user.campaigns.filter(active=True)[
                0
            ].name
        else:
            request.user.current_campaign = "RECOVERY MODE"
        request.user.save()
        return self.get_response(request)

    def __campaign_not_in_recovery_mode(self, request):
        campaign = Campaign.objects.get(name=request.user.current_campaign)
        if not campaign.active:
            if len(request.user.campaigns.filter(active=True)) != 0:
                request.user.current_campaign = request.user.campaigns.filter(
                    active=True
                )[0].name
            else:
                request.user.current_campaign = "RECOVERY MODE"
            request.user.save()
        return self.get_response(request)


class ClinicMessageMiddleware:
    """
    Defines middleware to check the current user's messages and deliver their current inbox count.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.message_number = len(
                Message.objects.filter(recipient=request.user).filter(read=False)
            )
        return self.get_response(request)


class CheckForSessionInvalidatedMiddleware:
    """
    Defines middleware to handle creation of new sessions if the current session is stale.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                request.user.logged_in_user.session_key = request.session.session_key
                request.user.logged_in_user.save()
            except fEMRUser.logged_in_user.RelatedObjectDoesNotExist:
                UserSession.objects.get_or_create(user=request.user)
        return self.get_response(request)
