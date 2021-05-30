from main.models import fEMRUser
from clinic_messages.form import MessageForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist

from clinic_messages.models import Message


def index(request):
    if request.user.is_authenticated:
        return render(request, 'messages/list/list.html', {
                'list_view': Message.objects.filter(recipient=request.user)
            })
    else:
        return redirect('main:not_logged_in')


def new_message(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save()
                message.sender = request.user
                message.save()
            return redirect('clinic_messages:index')
        else:
            form = MessageForm()
        return render(request, 'messages/message/new.html', {
            'form': form
        })
    else:
        return redirect('main:not_logged_in')


def reply_message(request, message_id=None, sender_id=None):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save()
                message.sender = request.user
                message.save()
            return redirect('clinic_messages:index')
        else:
            message = Message.objects.get(pk=message_id)
            message.read = True
            message.save()
            sender = fEMRUser.objects.get(pk=sender_id)
            form = MessageForm()
            form.initial['recipient'] = sender.pk
            form.initial['replied_to'] = message
        return render(request, 'messages/message/read.html', {
            'message': message,
            'sender': sender,
            'form': form
        })
    else:
        return redirect('main:not_logged_in')


def delete_message(request, message_id=None):
    if request.user.is_authenticated:
        data = Message.objects.all()
        try:
            p = get_object_or_404(Message, pk=id)
            Message.objects.filter(id=p.id).delete()
        except ObjectDoesNotExist:
            pass
        return render(request, 'list/patient.html',
                        {'user': request.user,
                        'list_view': data})
    else:
        return redirect('main:not_logged_in')