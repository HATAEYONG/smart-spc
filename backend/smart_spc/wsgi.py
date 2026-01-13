"""
WSGI config for Smart SPC project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_spc.settings')

application = get_wsgi_application()
