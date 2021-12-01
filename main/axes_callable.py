import os
from django.core.mail import send_mail
from django.shortcuts import render
from clinic_messages.models import Message
from main.models import fEMRUser


def user_locked_out_callback(request, credentials):
    user = fEMRUser.objects.filter(username=credentials["username"])
    if user.exists() and len(user) == 1:
        user = user[0]
        campaigns = user.campaigns.all()
        campaign_manager = campaigns[0].main_contact if len(campaigns) != 0 else None
        if campaign_manager:
            message = Message.objects.create(
                subject="User Locked Out",
                content=f"{user}, a user in one of your campaigns, is locked out of fEMR OnChain. You can wait 15 minutes and they'll unlock automatically, or else you can unlock them manually through the Campaign Manager tab.",
                sender=fEMRUser.objects.get(username="admin"),
                recipient=campaign_manager,
            )
            send_mail(
                f"Message from {message.sender}",
                f"{message.content}\n\n\nTHIS IS AN AUTOMATED MESSAGE. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO REPLY.",
                os.environ.get("DEFAULT_FROM_EMAIL"),
                [message.recipient.email],
            )
    return render(request, "auth/lockout.html", status=403)
