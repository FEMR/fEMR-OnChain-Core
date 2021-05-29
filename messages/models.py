from main.models import fEMRUser
from django.db import models


class Message(models.Model):
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=2500)

    sender = models.ForeignKey(fEMRUser, editable=False)
    recipient = models.ForeignKey(fEMRUser)

    replied_to = models.ForeignKey(
        "Message", blank=True, null=True, editable=False)

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.subject
