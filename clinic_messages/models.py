from main.models import fEMRUser
from django.db import models
from django.utils import timezone


class Message(models.Model):
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=2500)

    sender = models.ForeignKey(
        fEMRUser, on_delete=models.CASCADE, null=True, blank=True, editable=False, related_name='sender')
    recipient = models.ForeignKey(
        fEMRUser, on_delete=models.CASCADE, related_name='recipient')

    replied_to = models.ForeignKey(
        "Message", on_delete=models.CASCADE, blank=True, null=True, editable=False)

    read = models.BooleanField(default=False, editable=False)
    deleted_by_sender = models.BooleanField(default=False, editable=False)
    deleted_by_recipient = models.BooleanField(default=False, editable=False)

    timestamp = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False, default=timezone.now())

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.subject
