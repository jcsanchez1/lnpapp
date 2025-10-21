from django.apps import AppConfig


class ExamenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'examen'
    verbose_name = 'Sistema LNP'
    
    def ready(self):
        import examen.signals  # Importaremos signals después