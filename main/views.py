"""
View functions for top-level locations.
All views, except auth views and the index view, should be considered to check for a
valid and authenticated user.
If one is not found, they will direct to the appropriate error page.
"""
import json
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.mail import send_mail
from silk.profiling.profiler import silk_profile
from main.decorators import is_admin, is_authenticated
from main.forms import ForgotUsernameForm
from main.models import Campaign, MessageOfTheDay, fEMRUser


# noinspection PyUnusedLocal
def index(request):
    """
    Initial landing view.

    :param request: A Django request object.
    :return: A template rendered as an HTTPResponse.
    """
    return redirect("main:login_view")


@is_authenticated
@silk_profile("home")
def home(request):
    """
    The landing page for the authenticated user.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the home page.
    """
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
            "selected_campaign": request.user.current_campaign,
        },
    )


@is_authenticated
def library(request):
    """
    The root of the main library page, where clinical users of the application can view
    and manage the data models contained in the fEMR On-Chain database.

    :param request: Django Request object.
    :return: An HttpResponse, rendering the library page.
    """
    return render(request, "data/library.html", {"user": request.user})


# noinspection PyUnusedLocal
def healthcheck(request):
    """
    Returns a success message.
    """
    return HttpResponse("Working.")


@is_admin
@is_authenticated
def set_timezone(request):
    campaign = Campaign.objects.get(name=request.user.current_campaign)
    if request.method == "POST":
        request.session["django_timezone"] = request.POST["timezone"]
        campaign.timezone = request.POST["timezone"]
        campaign.save()
        return_response = redirect("main:index")
    else:
        selected_time_zone = campaign.timezone
        return_response = render(
            request,
            "data/timezone.html",
            {
                "selected_time_zone": selected_time_zone,
                "timezones": pytz.common_timezones,
            },
        )
    return return_response


def forgot_username(request):
    if request.method == "POST":
        try:
            user = fEMRUser.objects.get(email__iexact=request.POST["email"])
            # noinspection LongLine
            send_mail(
                "Username Recovery",
                "Someone recently requested a username reminder from fEMR On-Chain. "
                f"If this was you, your username is:\n\n\n {user.username}\n\n\n "
                "If it wasn't you, you "
                "can safely ignore this email.\n\n\nTHIS IS AN AUTOMATED MESSAGE "
                "FROM fEMR ON-CHAIN. "
                "PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO "
                "fEMR ON-CHAIN TO REPLY.",
                "noreply@teamfemr.org",
                [user.email],
            )
        except ObjectDoesNotExist:
            pass
        return_response = render(request, "data/username_sent.html")
    else:
        form = ForgotUsernameForm()
        return_response = render(request, "data/forgot_username.html", {"form": form})
    return return_response


@is_authenticated
def help_messages_off(request):
    request.session["tags_off"] = (
        None if request.session.get("tags_off", None) else True
    )
    return redirect(request.META.get("HTTP_REFERER", "/"))


# open .json file and convert it into a dictionary object, to display in the FAQs page:
def faqs(request):
    with open("main/static/main/js/faqs.json", "r", encoding="utf-8") as json_file:
        json_data = json_file.read()
        dictionary_object = json.loads(json_data)

    if request.user.is_authenticated:
        return_value = render(request, "data/faqs_auth.html", dictionary_object)
    else:
        return_value = render(request, "data/faqs.html", dictionary_object)
    return return_value
