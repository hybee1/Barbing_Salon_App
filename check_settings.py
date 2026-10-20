import os
import django
from django.conf import settings

from core_config import settings_base, settings_dev

print("DJANGO_SETTINGS_MODULE:", os.getenv("DJANGO_SETTINGS_MODULE"))
print("DEBUG:", settings_dev.DEBUG)
print("ALLOWED_HOSTS:", settings_dev.ALLOWED_HOSTS)
print("SETTINGS_MODULE:", settings.SETTINGS_MODULE)