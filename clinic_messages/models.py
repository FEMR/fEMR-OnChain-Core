from main.models import fEMRUser
from django.db import models


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

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.subject
