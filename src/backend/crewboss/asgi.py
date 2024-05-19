"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

import django
import sentry_sdk
from channels.routing import get_default_application
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.django import DjangoIntegration

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewboss.settings")
django.setup()

sentry_sdk.init(
    dsn="https://bdfbe6a56653447f8cad79c179e114ae@sentry.io/1544956",
    integrations=[DjangoIntegration()]
)
application = SentryAsgiMiddleware(get_default_application())
