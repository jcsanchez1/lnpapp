# examen/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User  # <-- AGREGAR ESTE IMPORT
from .models import Profile, Rol, Muestra

@receiver(post_save, sender=User)
def crear_profile_usuario(sender, instance, created, **kwargs):
    """
    Signal para crear automáticamente un Profile cuando se crea un User.
    Por defecto se asigna rol CAT (el más restrictivo).
    """
    if created:
        # Verificar si ya tiene profile
        if not hasattr(instance, 'profile'):
            # Obtener o crear rol por defecto (CAT)
            rol_default, _ = Rol.objects.get_or_create(
                nivel='CAT',
                defaults={
                    'nombre': 'Usuario Centro',
                    'descripcion': 'Usuario de centro de atención con acceso limitado'
                }
            )
            Profile.objects.create(user=instance, rol=rol_default)


@receiver(post_save, sender=User)
def guardar_profile_usuario(sender, instance, **kwargs):
    """Guardar el profile cuando se guarda el usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

# ==================== SIGNALS PARA SEMANA EPIDEMIOLÓGICA ====================

@receiver(post_save, sender=Muestra)
def actualizar_estadisticas_semana(sender, instance, created, **kwargs):
    """
    Actualiza las estadísticas cacheadas en SemanaEpidemiologica
    cuando se crea o modifica una Muestra.
    """
    if instance.semana_epidemiologica:
        semana = instance.semana_epidemiologica
        
        # Recalcular estadísticas
        muestras = semana.muestras.all()
        semana.total_muestras = muestras.count()
        semana.total_positivas = muestras.filter(resultado='POS').count()
        semana.total_negativas = muestras.filter(resultado='NEG').count()
        
        semana.save(update_fields=['total_muestras', 'total_positivas', 'total_negativas', 'fecha_actualizacion'])


@receiver(post_delete, sender=Muestra)
def actualizar_estadisticas_semana_eliminar(sender, instance, **kwargs):
    """
    Actualiza las estadísticas cuando se elimina una Muestra.
    """
    if instance.semana_epidemiologica:
        semana = instance.semana_epidemiologica
        
        # Recalcular estadísticas
        muestras = semana.muestras.all()
        semana.total_muestras = muestras.count()
        semana.total_positivas = muestras.filter(resultado='POS').count()
        semana.total_negativas = muestras.filter(resultado='NEG').count()
        
        semana.save(update_fields=['total_muestras', 'total_positivas', 'total_negativas', 'fecha_actualizacion'])