from main.templatetags.encounter_tags import temp_round


def test_round_temp():
    assert temp_round(2.188) == 2.19


def test_round_none():
    assert temp_round(None) == None
