from django.apps import AppConfig

# En apps.py de la aplicación usuarios:
class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        import usuarios.signals
    
    def ready(self):
        import usuarios.signals  # Para activar las señales