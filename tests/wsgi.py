"""
WSGI Configuration
"""
import os

from django.core.wsgi import get_wsgi_application

# This allows easy placement of apps within the interior
# src directory.


MAIN_SETTINGS = "tests.settings"

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
os.environ.setdefault = MAIN_SETTINGS

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()
