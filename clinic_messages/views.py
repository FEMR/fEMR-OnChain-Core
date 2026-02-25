import os

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from clinic_messages.form import MessageForm
from clinic_messages.models import Message
from clinic_messages.decorators import is_authenticated

User = get_user_model()


@is_authenticated
def index(request):
    data = (
        Message.objects.filter(recipient=request.user)
        .filter(deleted_by_recipient=False)
        .order_by("-timestamp")
    )
    paginator = Paginator(data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "messages/list/list.html",
        {"list_view": page_obj},
    )


@is_authenticated
def sent_box(request):
    data = (
        Message.objects.filter(sender=request.user)
        .filter(deleted_by_sender=False)
        .order_by("-timestamp")
    )
    paginator = Paginator(data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "messages/list/sent_list.html",
        {"list_view": page_obj},
    )


@is_authenticated
def new_message(request, sender_id=None):
    if request.method == "POST":
        form = MessageForm(request.POST)
        form.fields["recipient"].queryset = User.objects.filter(is_active=True)
        if form.is_valid():
            message = form.save()
            message.sender = request.user
            message.save()
            send_mail(
                f"Message from {message.sender}",
                # pylint: disable=C0301
                f"{message.content}\n\n\nTHIS IS AN AUTOMATED MESSAGE. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO REPLY.",
                os.environ.get("DEFAULT_FROM_EMAIL"),
                [message.recipient.email],
            )
            return_response = render(request, "messages/message/success.html")
        else:
            return_response = render(
                request, "messages/message/new.html", {"form": form}
            )
    else:
        form = MessageForm()
        if sender_id is not None:
            form.initial["recipient"] = User.objects.get(pk=sender_id)
        form.fields["recipient"].queryset = User.objects.filter(is_active=True)
        return_response = render(request, "messages/message/new.html", {"form": form})
    return return_response


@is_authenticated
def reply_message(request, message_id=None, sender_id=None):
    if request.method == "POST":
        form = MessageForm(request.POST)
        form.fields["recipient"].queryset = User.objects.filter(is_active=True)
        if form.is_valid():
            message = form.save()
            message.sender = request.user
            message.save()
            send_mail(
                f"Message from {message.sender}",
                # pylint: disable=C0301
                f"{message.content}\n\n\nTHIS IS AN AUTOMATED MESSAGE. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO REPLY.",
                os.environ.get("DEFAULT_FROM_EMAIL"),
                [message.recipient.email],
            )
            return_response = render(request, "messages/message/success.html")
        else:
            sender = User.objects.get(pk=sender_id)
            return_response = render(
                request,
                "messages/message/read.html",
                {"message": message, "sender": sender, "form": form},
            )
    else:
        message = Message.objects.get(pk=message_id)
        message.read = True
        message.save()
        sender = User.objects.get(pk=sender_id)
        form = MessageForm()
        form.initial["recipient"] = sender.pk
        form.initial["subject"] = "RE: " + str(message.subject)
        form.initial["replied_to"] = message
        form.fields["recipient"].queryset = User.objects.filter(is_active=True)
        return_response = render(
            request,
            "messages/message/read.html",
            {"message": message, "sender": sender, "form": form},
        )
    return return_response


@is_authenticated
def view_message(request, message_id=None):
    if request.method == "POST":
        form = MessageForm(request.POST)
        form.fields["recipient"].queryset = User.objects.filter(is_active=True)
        if form.is_valid():
            message = form.save()
            message.sender = request.user
            message.save()
        return_response = redirect("clinic_messages:index")
    else:
        message = Message.objects.get(pk=message_id)
        form = MessageForm()
        form.initial["recipient"] = message.recipient
        form.initial["replied_to"] = message
        form.fields["recipient"].queryset = User.objects.filter(is_active=True)
        return_response = render(
            request,
            "messages/message/sent.html",
            {"message": message, "sender": request.user, "form": form},
        )
    return return_response


@is_authenticated
def delete_message(_, message_id=None):
    message = get_object_or_404(Message, pk=message_id)
    message.deleted_by_recipient = True
    message.save()
    return redirect("clinic_messages:index")


@is_authenticated
def delete_sent_message(_, message_id=None):
    message = get_object_or_404(Message, pk=message_id)
    message.deleted_by_sender = True
    message.save()
    return redirect("clinic_messages:sent_box")
