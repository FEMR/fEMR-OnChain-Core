from main.apps import MainConfig


def test_main_config():
    assert MainConfig.name, 'main'
