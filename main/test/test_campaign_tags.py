from model_bakery import baker

from main.templatetags.campaign_tags import is_selected


def test_is_selected():
    c = baker.make('main.Campaign')
    s = c.name
    assert is_selected(c, s)


def test_is_not_selected():
    c = baker.make('main.Campaign')
    s = "Test"
    assert not is_selected(c, s)
