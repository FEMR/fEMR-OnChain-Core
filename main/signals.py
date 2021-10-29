import os
from django.conf import settings
from django.contrib.auth import user_logged_in, user_logged_out
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from axes.signals import user_locked_out
from clinic_messages.models import Message

from main.femr_admin_views import get_client_ip
from main.models import Campaign, AuditEntry, fEMRUser


@receiver(user_locked_out)
def user_locked_out_callback(sender, request, user, **kwargs):
    campaigns = user.campaigns.all()
    campaign_manager = campaigns[0] if len(campaigns) != 0 else None
    if campaign_manager:
        message = Message.objects.create(
            subject="User Locked Out",
            content=f"{user}, a user in one of your campaigns, "
            "is locked out of fEMR OnChain. You can wait 15 minutes "
            "and they'll unlock automatically, or else you can "
            "unlock them manually through the Campaign Manager tab.",
            sender=fEMRUser.objecs.get(username="admin"),
            recipient=campaign_manager,
        )
        send_mail(
            f"Message from {message.sender}",
            f"{message.content}\n\n\nTHIS IS AN AUTOMATED MESSAGE. "
            "PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO REPLY.",
            os.environ.get("DEFAULT_FROM_EMAIL"),
            [message.recipient.email],
        )


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    campaign_list = request.user.campaigns.filter(active=True)
    if len(campaign_list) != 0:
        name = campaign_list[0].name
        campaign = Campaign.objects.get(name=name)
    else:
        campaign = None
    AuditEntry.objects.create(
        action="user_logged_in", ip=ip, username=user.username, campaign=campaign
    )


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    try:
        campaign_list = request.user.campaigns.filter(active=True)
        if len(campaign_list) != 0:
            name = campaign_list[0].name
            campaign = Campaign.objects.get(name=name)
        else:
            campaign = None
        AuditEntry.objects.create(
            action="user_logged_out", ip=ip, username=user.username, campaign=campaign
        )
    except AttributeError:
        pass


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    A general-purpose, commonly-used function generating
    authentication tokens for the RESTful API.

    Like any other view, this is never called directly and
    should be handled by the URL conf for djangorestframework.

    :param sender: Origin of the request.
    :param instance: The user to generate a Token for.
    :param created: Used to determine if a Token already exists for the given user.
    :param kwargs: Should be empty.
    """
    if created:
        # noinspection PyUnresolvedReferences
        Token.objects.create(user=instance)
