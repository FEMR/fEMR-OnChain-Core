from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

statuses = (
    ("1", "Waiting"),
    ("2", "Seen"),
    ("3", "Confirmed"),
    ("4", "In Progress"),
    ("5", "Resolved"),
    ("6", "Verified"),
)


class Comment(models.Model):
    """
    Database model for comments on SupportTickets.
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.CharField(max_length=256)
    timestamp = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False
    )
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)


class SupportTicket(models.Model):
    """
    Database model for support tickets.
    """

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    title = models.CharField(max_length=32)
    description = models.CharField(max_length=256)

    status = models.CharField(max_length=32, choices=statuses, null=True, blank=True)
    comments = models.ManyToManyField(Comment)

    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)

    timestamp = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False
    )
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.title)

    def __repr__(self):
        return repr(self.title)
