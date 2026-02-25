from datetime import timedelta

from django.utils.timezone import now
from model_bakery import baker

from app_mr.background_tasks import check_old_tickets
from app_mr.models import User, SupportTicket


def test_check_old_tickets_not_expired():
    s = baker.make("app_mr.SupportTicket")
    s.comments.add(baker.make("app_mr.Comment"))
    check_old_tickets()
    assert s.active


def test_check():
    User.objects.create()
    s = baker.make("app_mr.SupportTicket")
    s.comments.add(baker.make("app_mr.Comment"))
    n = now() + timedelta(days=35)
    check_old_tickets(now=n)
    n = SupportTicket.objects.get(title=s.title)
    assert not n.active
