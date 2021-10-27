"""
Handles top-level app configuration.
"""
import django.apps


class MainConfig(django.apps.AppConfig):
    """
    App Configuration Object
    """

    name = "main"

    def ready(self):
        import main.signals
