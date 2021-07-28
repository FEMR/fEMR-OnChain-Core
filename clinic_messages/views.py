import os
from main.models import fEMRUser
from clinic_messages.form import MessageForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail

from clinic_messages.models import Message


def index(request):
    if request.user.is_authenticated:
        return render(request, 'messages/list/list.html', {
            'list_view': Message.objects.filter(recipient=request.user).filter(deleted_by_recipient=False).order_by('-timestamp')
        })
    else:
        return redirect('main:not_logged_in')


def sent_box(request):
    if request.user.is_authenticated:
        return render(request, 'messages/list/sent_list.html', {
            'list_view': Message.objects.filter(sender=request.user).filter(deleted_by_sender=False).order_by('-timestamp')
        })
    else:
        return redirect('main:not_logged_in')


def new_message(request, sender_id=None):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = MessageForm(request.POST)
            form.fields['recipient'].queryset = fEMRUser.objects.filter(
                is_active=True)
            if form.is_valid():
                message = form.save()
                message.sender = request.user
                message.save()
                send_mail(
                    "Message from {0}".format(message.sender),
                    "{0}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.".format(message.content),
                    os.environ.get('DEFAULT_FROM_EMAIL'),
                    [message.recipient.email])
            return redirect('clinic_messages:index')
        else:
            form = MessageForm()
            if sender_id is not None:
                form.initial['recipient'] = fEMRUser.objects.get(pk=sender_id)
            form.fields['recipient'].queryset = fEMRUser.objects.filter(
                is_active=True)
        return render(request, 'messages/message/new.html', {
            'form': form
        })
    else:
        return redirect('main:not_logged_in')


def reply_message(request, message_id=None, sender_id=None):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = MessageForm(request.POST)
            form.fields['recipient'].queryset = fEMRUser.objects.filter(
                is_active=True)
            if form.is_valid():
                message = form.save()
                message.sender = request.user
                message.save()
                send_mail(
                    "Message from {0}".format(message.sender),
                    "{0}\n\n\nTHIS IS AN AUTOMATED MESSAGE FROM fEMR ON-CHAIN. PLEASE DO NOT REPLY TO THIS EMAIL. PLEASE LOG IN TO fEMR ON-CHAIN TO REPLY.".format(
                        message.content),
                    os.environ.get('DEFAULT_FROM_EMAIL'),
                    [message.recipient.email])
            return redirect('clinic_messages:index')
        else:
            message = Message.objects.get(pk=message_id)
            message.read = True
            message.save()
            sender = fEMRUser.objects.get(pk=sender_id)
            form = MessageForm()
            form.initial['recipient'] = sender.pk
            form.initial['replied_to'] = message
            form.fields['recipient'].queryset = fEMRUser.objects.filter(
                is_active=True)
        return render(request, 'messages/message/read.html', {
            'message': message,
            'sender': sender,
            'form': form
        })
    else:
        return redirect('main:not_logged_in')


def view_message(request, message_id=None, sender_id=None):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = MessageForm(request.POST)
            form.fields['recipient'].queryset = fEMRUser.objects.filter(
                is_active=True)
            if form.is_valid():
                message = form.save()
                message.sender = request.user
                message.save()
            return redirect('clinic_messages:index')
        else:
            message = Message.objects.get(pk=message_id)
            form = MessageForm()
            form.initial['recipient'] = message.recipient
            form.initial['replied_to'] = message
            form.fields['recipient'].queryset = fEMRUser.objects.filter(
                is_active=True)
        return render(request, 'messages/message/sent.html', {
            'message': message,
            'sender': request.user,
            'form': form
        })
    else:
        return redirect('main:not_logged_in')


def delete_message(request, id=None):
    if request.user.is_authenticated:
        p = get_object_or_404(Message, pk=id)
        p.deleted_by_recipient = True
        p.save()
        return redirect('clinic_messages:index')
    else:
        return redirect('main:not_logged_in')


def delete_sent_message(request, id=None):
    if request.user.is_authenticated:
        p = get_object_or_404(Message, pk=id)
        p.deleted_by_sender = True
        p.save()
        return redirect('clinic_messages:sent_box')
    else:
        return redirect('main:not_logged_in')
