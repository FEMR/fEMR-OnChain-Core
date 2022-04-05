from django.conf import settings
from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from app_mr.models import SupportTicket
from app_mr.signals import ticket_activity
from clinic_messages.models import Message

from main.femr_admin_views import get_client_ip
from main.models import Campaign, AuditEntry, fEMRUser


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    campaign_list = request.user.campaigns.filter(active=True)
    if len(campaign_list) != 0:
        name = campaign_list[0].name
        campaign = Campaign.objects.get(name=name)
    else:
        campaign = None
    AuditEntry.objects.create(
        action="user_logged_in",
        ip=get_client_ip(request),
        username=user.username,
        campaign=campaign,
        browser_user_agent=request.user_agent.browser.family,
    )


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    try:
        campaign_list = request.user.campaigns.filter(active=True)
        if len(campaign_list) != 0:
            name = campaign_list[0].name
            campaign = Campaign.objects.get(name=name)
        else:
            campaign = None
        AuditEntry.objects.create(
            action="user_logged_out",
            ip=get_client_ip(request),
            username=user.username,
            campaign=campaign,
            browser_user_agent=request.user_agent.browser.family,
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


@receiver(ticket_activity)
def handle_ticket_activity(sender, ticket, **kwargs):
    ticket = SupportTicket.objects.get(pk=ticket)
    for user in Group.objects.get(name="Developer").user_set.all():
        Message.objects.create(
            subject="Ticket Update",
            content=f"This message is to let you know that an update was posted to ticket {ticket.id}. Use the Let Us Know link to view the new information.",
            sender=fEMRUser.objects.get(username="admin"),
            recipient=user,
        )
