"""
WSGI config for pubcrawler project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

path = '/home/wspek/Code/private/socialdata/website'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialdata_site.settings")
os.environ['HTTPS'] = "on"

application = get_wsgi_application()
