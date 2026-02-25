from model_bakery import baker

from clinic_messages.models import Message, User


def test_message():
    m = baker.make("clinic_messages.Message")
    assert str(m) == m.subject


def test_is_message():
    u = User.objects.get(pk=1)
    m = Message.objects.create(
        subject="Test",
        content="Test",
        recipient=u,
    )
    assert isinstance(m, Message)
    assert m.subject == "Test"
