
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core_config.settings_dev",
)

django.setup()

from django.conf import settings
import core_config.settings_dev as dev_settings

print("DEBUG:", settings.DEBUG)
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
print("Module DEBUG:", dev_settings.DEBUG)
print("Module ALLOWED_HOSTS:", dev_settings.ALLOWED_HOSTS)
print("Settings file:", settings.SETTINGS_MODULE)
