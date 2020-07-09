import os
import django
import channels.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "charles.settings")
django.setup()
application = channels.routing.get_default_application()
