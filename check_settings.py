
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core_config.settings_dev",
)

django.setup()

from django.conf import settings

print("Settings module:", os.environ["DJANGO_SETTINGS_MODULE"])
print("DEBUG:", settings.DEBUG)
print("ALLOWED_HOSTS:", repr(settings.ALLOWED_HOSTS))
print("ALLOWED_HOSTS type:", type(settings.ALLOWED_HOSTS).__name__)
print("OpenTelemetry service:", os.getenv("OTEL_SERVICE_NAME"))
