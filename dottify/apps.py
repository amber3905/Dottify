from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DottifyConfig(AppConfig):
    """
    Application configuration for the dottify sub-app.

    If we needed to hook into Django's startup (e.g. to create default
    groups or permissions) we would wire post_migrate signals from here.
    For the coursework, the default behaviour is sufficient.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dottify'
