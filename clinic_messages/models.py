from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Message(models.Model):
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=2500)

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=False,
        related_name="sender",
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient"
    )

    replied_to = models.ForeignKey(
        "Message", on_delete=models.CASCADE, blank=True, null=True, editable=False
    )

    read = models.BooleanField(default=False, editable=False)
    deleted_by_sender = models.BooleanField(default=False, editable=False)
    deleted_by_recipient = models.BooleanField(default=False, editable=False)

    timestamp = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False
    )

    def __str__(self):
        return str(self.subject)
