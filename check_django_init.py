import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core_config.settings_dev",
)

django.setup()

from django.conf import settings

print("Configured:", settings.configured)
print("Settings module:", getattr(settings, "SETTINGS_MODULE", None))
print("DEBUG:", settings.DEBUG)
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)