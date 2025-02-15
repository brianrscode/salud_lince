from django.apps import AppConfig


class ConsultasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consultas'

    def ready(self):
        import consultas.signals