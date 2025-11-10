# examen/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Profile, Rol, Muestra, SemanaEpidemiologica, ConfiguracionAlerta, Alerta


# ==================== SIGNALS DE USUARIO ====================

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


# ==================== SIGNALS PARA ALERTAS EPIDEMIOLÓGICAS ====================

@receiver(post_save, sender=Muestra)
def detectar_alertas_epidemiologicas(sender, instance, created, **kwargs):
    """
    Detecta automáticamente alertas epidemiológicas cuando se registra una muestra positiva.
    
    FLUJO:
    1. Verifica que la muestra sea positiva
    2. Obtiene los parásitos encontrados
    3. Por cada parásito, busca si hay configuración de alerta activa
    4. Cuenta casos recientes en la ventana de tiempo
    5. Determina el nivel de alerta según umbrales
    6. Crea o actualiza la alerta correspondiente
    """
    
    # Solo procesar muestras positivas
    if instance.resultado != 'POS':
        return
    
    # Obtener parásitos encontrados en esta muestra
    parasitos_encontrados = instance.get_parasitos_encontrados()
    
    # Por cada parásito encontrado, verificar si hay alerta configurada
    for parasito_nombre, estadio in parasitos_encontrados.items():
        
        # Mapeo de nombres legibles a campos del modelo
        mapeo_parasitos = {
            'Entamoeba histolytica': 'entamoeba_histolytica',
            'Entamoeba coli': 'entamoeba_coli',
            'Entamoeba hartmanni': 'entamoeba_hartmanni',
            'Endolimax nana': 'endolimax_nana',
            'Iodamoeba bütschlii': 'iodamoeba_butschlii',
            'Giardia intestinalis': 'giardia_intestinalis',
            'Pentatrichomonas hominis': 'pentatrichomonas_hominis',
            'Chilomastix mesnili': 'chilomastix_mesnili',
            'Balantidium coli': 'balantidium_coli',
            'Blastocystis sp': 'blastocystis_sp',
            'Cystoisospora belli': 'cystoisospora_belli',
            'Cyclospora cayetanensis': 'cyclospora_cayetanensis',
            'Cryptosporidium spp': 'cryptosporidium_spp',
            'Ascaris lumbricoides': 'ascaris_lumbricoides',
            'Trichuris trichiura': 'trichuris_trichiura',
            'Necator americanus': 'necator_americanus',
            'Strongyloides stercoralis': 'strongyloides_stercoralis',
            'Enterobius vermicularis': 'enterobius_vermicularis',
            'Taenia spp': 'taenia_spp',
            'Hymenolepis diminuta': 'hymenolepis_diminuta',
            'Rodentolepis nana': 'rodentolepis_nana',
        }
        
        parasito_campo = mapeo_parasitos.get(parasito_nombre)
        if not parasito_campo:
            continue  # Parásito no mapeado, saltar
        
        # Buscar configuración de alerta activa para este parásito
        try:
            config = ConfiguracionAlerta.objects.get(
                parasito_campo=parasito_campo,
                activo=True
            )
        except ConfiguracionAlerta.DoesNotExist:
            continue  # No hay alerta configurada para este parásito
        
        # Calcular ventana de tiempo
        fecha_inicio = instance.fecha_examen - timedelta(days=config.ventana_tiempo_dias)
        
        # Contar casos recientes en el centro en la ventana de tiempo
        casos_ventana = Muestra.objects.filter(
            centro_atencion=instance.centro_atencion,
            fecha_examen__gte=fecha_inicio,
            fecha_examen__lte=instance.fecha_examen,
            resultado='POS',
            **{f'{parasito_campo}__isnull': False}
        ).exclude(**{parasito_campo: ''}).count()
        
        # Contar casos en el día actual
        casos_dia = Muestra.objects.filter(
            centro_atencion=instance.centro_atencion,
            fecha_examen=instance.fecha_examen,
            resultado='POS',
            **{f'{parasito_campo}__isnull': False}
        ).exclude(**{parasito_campo: ''}).count()
        
        # Determinar nivel de alerta (evaluar de mayor a menor gravedad)
        nivel = None
        if casos_ventana >= config.umbral_emergencia:
            nivel = 'ROJO'
        elif casos_ventana >= config.umbral_alerta:
            nivel = 'NARANJA'
        elif casos_ventana >= config.umbral_precaucion:
            nivel = 'AMARILLO'
        else:
            # No alcanza ningún umbral, no crear alerta
            continue
        
        # Verificar si ya existe una alerta ACTIVA para este parásito en este centro
        alerta_existente = Alerta.objects.filter(
            configuracion=config,
            centro_atencion=instance.centro_atencion,
            estado__in=['ACTIVA', 'EN_PROCESO']
        ).first()
        
        if alerta_existente:
            # ACTUALIZAR alerta existente
            alerta_existente.numero_casos = casos_ventana
            alerta_existente.numero_casos_dia = casos_dia
            alerta_existente.nivel = nivel
            alerta_existente.save()
            
        else:
            # CREAR nueva alerta
            Alerta.objects.create(
                configuracion=config,
                muestra_origen=instance,
                nivel=nivel,
                estado='ACTIVA',
                centro_atencion=instance.centro_atencion,
                region=instance.centro_atencion.region,
                numero_casos=casos_ventana,
                numero_casos_dia=casos_dia
            )