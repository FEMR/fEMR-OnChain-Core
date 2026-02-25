from model_bakery import baker


def test_support_ticket():
    st = baker.make("app_mr.SupportTicket")
    assert str(st) == st.title
