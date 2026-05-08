from django.apps import AppConfig


class InspectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inspections'
    verbose_name = 'نظام تقييم المنشآت الغذائية'

    def ready(self):
        # Auto-seed reference data on first startup if tables are empty.
        try:
            from django.db import connection
            tables = connection.introspection.table_names()
            if 'inspections_section' not in tables:
                return
            from .models import Section
            if Section.objects.count() == 0:
                from django.core.management import call_command
                call_command('seed_governorates', verbosity=0)
                call_command('seed_items', verbosity=0)
        except Exception:
            pass
