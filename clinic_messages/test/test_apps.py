from clinic_messages.apps import MessagesConfig


def test_main_config():
    assert MessagesConfig.name == "clinic_messages"
