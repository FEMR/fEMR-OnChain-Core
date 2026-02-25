"""
Non-view functions used to carry out background processes.
"""
from datetime import timedelta

from django.utils import timezone

from app_mr.models import Comment, SupportTicket, User


def check_old_tickets(now=None) -> None:
    """
    Close tickets with no activity for 30 days.
    :param now:
    :return:
    """
    if now is None:
        now = timezone.now()
    delta = now - timedelta(days=30)
    for ticket in SupportTicket.objects.filter(active=True):
        if ticket.last_updated < delta:
            ticket.comments.add(
                Comment.objects.create(
                    author=User.objects.get(pk=1),
                    comment="Hi all - we haven't seen activity on this ticket for 30 days, "
                    "so we're going to mark it as resolved. Please don't hesitate to open a "
                    "new ticket if you need more help. ",
                )
            )
            ticket.status = "5"
            ticket.active = False
            ticket.save()
