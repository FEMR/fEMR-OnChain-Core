from main.templatetags.help_tags import is_help_off


def test_is_help_off_true():
    session = {
        "tags_off": True,
    }
    assert is_help_off(session)


def test_is_help_off_false():
    session = dict()
    assert not is_help_off(session)
