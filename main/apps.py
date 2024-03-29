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
        # pylint: disable=W0611,C0415
        import main.signals
