"""
View functions for top-level locations.
All views, except auth views and the index view, should be considered to check for a valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
from os import name
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from main.background_tasks import run_encounter_close
from silk.profiling.profiler import silk_profile
from django.utils import timezone

from main.forms import ForgotUsernameForm
from main.models import Campaign, MessageOfTheDay, Photo, fEMRUser


# noinspection PyUnusedLocal
def index(request):
    """
    Initial landing view.

    :param request: A Django request object.
    :return: A template rendered as an HTTPResponse.
    """
    return redirect("main:login_view")


@silk_profile("home")
def home(request):
    """
    The landing page for the authenticated user.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the home page.
    """
    if request.user.is_authenticated:
        run_encounter_close(Campaign.objects.get(name=request.session["campaign"]))
        motd = MessageOfTheDay.load()
        if motd.start_date is not None or motd.end_date is not None:
            if motd.start_date < timezone.now().date() < motd.end_date:
                motd_final = motd.text
            else:
                motd_final = ""
        else:
            motd_final = ""
        return render(
            request,
            "data/home.html",
            {
                "user": request.user,
                "page_name": "Home",
                "campaigns": request.user.campaigns.filter(active=True),
                "motd": motd_final,
                "selected_campaign": request.session["campaign"],
            },
        )
    else:
        return redirect("main:not_logged_in")


def library(request):
    """
    The root of the main library page, where clinical users of the application can view
    and manage the data models contained in the fEMR On-Chain database.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the library page.
    """
    if request.user.is_authenticated:
        return render(request, "data/library.html", {"user": request.user})
    else:
        return redirect("main:not_logged_in")


# noinspection PyUnusedLocal
def healthcheck(request):
    """
    Returns a success message.
    """
    return HttpResponse("Working.")


def set_timezone(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="Admin").exists():
            campaign = Campaign.objects.get(name=request.session["campaign"])
            if request.method == "POST":
                request.session["django_timezone"] = request.POST["timezone"]
                campaign.timezone = request.POST["timezone"]
                campaign.save()
                return redirect("main:index")
            else:
                selected_time_zone = campaign.timezone
                return render(
                    request,
                    "data/timezone.html",
                    {
                        "selected_time_zone": selected_time_zone,
                        "timezones": pytz.common_timezones,
                    },
                )
        else:
            return redirect("main:permission_denied")
    else:
        return redirect("main:not_logged_in")


def forgot_username(request):
    if request.method == "POST":
        try:
            user = fEMRUser.objects.get(email__iexact=request.POST["email"])
            from django.core.mail import send_mail

            # noinspection LongLine
            send_mail(
                "Username Recovery",
                "Someone recently requested a username reminder from fEMR On-Chain. If this was you, your username is:\n\n\n {}\n\n\n If it wasn't you, you can safely ignore this email.\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.".format(
                    user.username
                ),
                "noreply@teamfemr.org",
                [user.email],
            )
        except ObjectDoesNotExist:
            pass
        return render(request, "data/username_sent.html")
    else:
        form = ForgotUsernameForm()
        return render(request, "data/forgot_username.html", {"form": form})


def help_messages_off(request):
    if request.user.is_authenticated:
        request.session["tags_off"] = (
            None if request.session.get("tags_off", None) else True
        )
        return redirect(request.META.get("HTTP_REFERER", "/"))
    else:
        return redirect("main:not_logged_in")
