"""
WSGI config for femr_onchain project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "femr_onchain.settings")

application = get_wsgi_application()
