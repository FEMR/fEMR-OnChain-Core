from app_mr.apps import AppMRConfig


def test_main_config():
    assert AppMRConfig.name == "app_mr"
