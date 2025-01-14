from django.contrib import admin
from .models import Expediente, Region, CentroAtencion, Profile, Muestra


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre', 'apellido', 'sexo', 'fecha_creacion', 'fecha_modificacion')
    search_fields = ('dni', 'nombre', 'apellido')
    list_filter = ('sexo', 'fecha_creacion', 'fecha_modificacion')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('numero_region', 'nombre')
    search_fields = ('nombre',)
    list_filter = ('numero_region',)


@admin.register(CentroAtencion)
class CentroAtencionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'region')
    search_fields = ('nombre', 'direccion')
    list_filter = ('region',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'centro_atencion')
    search_fields = ('user__username', 'centro_atencion__nombre')
    list_filter = ('centro_atencion',)


@admin.register(Muestra)
class MuestraAdmin(admin.ModelAdmin):
    list_display = (
        'fecha', 'Expediente', 'Edad', 'consistencia', 'moco',
        'sangre_macroscopica', 'Intensidad_de_la_Infección_KATO_KATZ', 'No_se_observaron_parásitos'
    )
    search_fields = (
        'Expediente__dni', 'Expediente__nombre', 
        'Expediente__apellido'
    )
    list_filter = (
        'fecha', 'consistencia', 'moco', 
        'sangre_macroscopica', 'Intensidad_de_la_Infección_KATO_KATZ', 
        'No_se_observaron_parásitos'
    )
    list_editable = ('consistencia', 'moco', 'sangre_macroscopica')
