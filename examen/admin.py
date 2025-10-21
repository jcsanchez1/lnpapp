from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    Region, 
    CentroAtencion, 
    Rol, 
    Profile, 
    Expediente, 
    Muestra,
    Departamento,
    Municipio
)

# ==================== DEPARTAMENTO ====================

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'extension_territorial', 'cantidad_municipios', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)
    
    readonly_fields = ('fecha_creacion',)
    
    def cantidad_municipios(self, obj):
        count = obj.municipios.count()
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    cantidad_municipios.short_description = 'Municipios'


# ==================== MUNICIPIO ====================

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'departamento', 'es_cabecera', 'activo')
    list_filter = ('departamento', 'es_cabecera', 'activo')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)
    
    readonly_fields = ('fecha_creacion',)

# ==================== INLINE PARA PROFILE EN USER ====================

class ProfileInline(admin.StackedInline):
    """Inline para editar Profile dentro de User"""
    model = Profile
    can_delete = False
    verbose_name = 'Perfil del Usuario'
    verbose_name_plural = 'Perfil'
    
    fieldsets = (
        ('Rol y Permisos', {
            'fields': ('rol', 'activo')
        }),
        ('Asignación Geográfica', {
            'fields': ('region', 'centro_atencion'),
            'description': (
                '<strong>Instrucciones:</strong><br>'
                '• <strong>LNP:</strong> No asignar región ni centro<br>'
                '• <strong>REG:</strong> Asignar solo región<br>'
                '• <strong>CAT:</strong> Asignar región primero, luego el centro se filtrará automáticamente'
            )
        }),
        ('Información Adicional', {
            'fields': ('telefono', 'cargo'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('ultimo_acceso', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'ultimo_acceso')


# ==================== EXTENDER USER ADMIN ====================

class UserAdmin(BaseUserAdmin):
    """Extender el admin de User para incluir Profile"""
    inlines = (ProfileInline,)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'get_centro', 'is_active')
    list_filter = ('is_active', 'is_staff', 'profile__rol__nivel')
    
    def get_rol(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.rol.nombre
        return '-'
    get_rol.short_description = 'Rol'
    
    def get_centro(self, obj):
        if hasattr(obj, 'profile') and obj.profile.centro_atencion:
            return obj.profile.centro_atencion.nombre
        return '-'
    get_centro.short_description = 'Centro'


# Re-registrar User con el nuevo admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ==================== REGIÓN ====================

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('numero_region', 'nombre', 'cantidad_centros', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre', 'numero_region')
    ordering = ('numero_region',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_region', 'nombre')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion'),
        }),
    )
    
    readonly_fields = ('fecha_creacion',)
    
    def cantidad_centros(self, obj):
        count = obj.centros_atencion.count()
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    cantidad_centros.short_description = 'Centros'


# ==================== CENTRO DE ATENCIÓN ====================

@admin.register(CentroAtencion)
class CentroAtencionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'region', 'es_regional', 'cantidad_expedientes', 'cantidad_muestras', 'activo')
    list_filter = ('region', 'es_regional', 'activo')
    search_fields = ('codigo', 'nombre', 'direccion')
    ordering = ('region', 'nombre')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'region', 'es_regional')
        }),
        ('Ubicación y Contacto', {
            'fields': ('direccion', 'telefono')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion'),
        }),
    )
    
    readonly_fields = ('fecha_creacion',)
    
    def cantidad_expedientes(self, obj):
        count = obj.expedientes.count()
        color = '#007bff' if count > 0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, count
        )
    cantidad_expedientes.short_description = 'Expedientes'
    
    def cantidad_muestras(self, obj):
        count = obj.muestras.count()
        color = '#17a2b8' if count > 0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, count
        )
    cantidad_muestras.short_description = 'Muestras'


# ==================== ROL ====================

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'cantidad_usuarios', 'permisos_resumidos', 'activo')
    list_filter = ('nivel', 'activo')
    search_fields = ('nombre', 'descripcion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nivel', 'descripcion')
        }),
        ('Permisos', {
            'fields': (
                'puede_crear_usuarios',
                'puede_ver_todas_regiones',
                'puede_generar_reportes_nacionales',
                'puede_editar_configuracion'
            )
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion'),
        }),
    )
    
    readonly_fields = ('fecha_creacion',)
    
    def cantidad_usuarios(self, obj):
        count = obj.usuarios.count()
        return format_html(
            '<span style="background-color: #6f42c1; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    cantidad_usuarios.short_description = 'Usuarios'
    
    def permisos_resumidos(self, obj):
        permisos = []
        if obj.puede_crear_usuarios:
            permisos.append('👥')
        if obj.puede_ver_todas_regiones:
            permisos.append('🌎')
        if obj.puede_generar_reportes_nacionales:
            permisos.append('📊')
        if obj.puede_editar_configuracion:
            permisos.append('⚙️')
        
        return ' '.join(permisos) if permisos else '—'
    permisos_resumidos.short_description = 'Permisos'


# ==================== PROFILE ====================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'get_region_display', 'centro_atencion', 'activo', 'ultimo_acceso')
    list_filter = ('rol__nivel', 'activo', 'region')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'cargo')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'rol')
        }),
        ('Asignación Geográfica', {
            'fields': ('region', 'centro_atencion'),
            'description': (
                '<div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 10px;">'
                '<strong>⚠️ Instrucciones Importantes:</strong><br>'
                '• <strong>LNP:</strong> No asignar región ni centro<br>'
                '• <strong>REG:</strong> Asignar solo región<br>'
                '• <strong>CAT:</strong> <u>Seleccionar región primero</u>, luego el centro se filtrará automáticamente'
                '</div>'
            )
        }),
        ('Información Adicional', {
            'fields': ('telefono', 'cargo')
        }),
        ('Estado y Auditoría', {
            'fields': ('activo', 'ultimo_acceso', 'fecha_creacion', 'fecha_modificacion'),
        }),
    )
    
    readonly_fields = ('ultimo_acceso', 'fecha_creacion', 'fecha_modificacion')
    
    def get_region_display(self, obj):
        if obj.region:
            return f"Región {obj.region.numero_region}"
        elif obj.centro_atencion:
            return f"Región {obj.centro_atencion.region.numero_region} (vía centro)"
        return '-'
    get_region_display.short_description = 'Región'


# ==================== EXPEDIENTE ====================

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = (
        'dni', 
        'nombre_completo_display', 
        'sexo', 
        'edad_display', 
        'centro_atencion', 
        'cantidad_muestras',
        'fecha_creacion'
    )
    list_filter = ('sexo', 'centro_atencion', 'departamento', 'activo')
    search_fields = ('dni', 'primer_nombre', 'primer_apellido', 'municipio')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Identificación', {
            'fields': ('dni',)
        }),
        ('Nombres', {
            'fields': (
                ('primer_nombre', 'segundo_nombre'),
                ('primer_apellido', 'segundo_apellido')
            )
        }),
        ('Datos Demográficos', {
            'fields': (
                ('sexo', 'fecha_nacimiento'),
            )
        }),
        ('Ubicación', {
            'fields': (
                ('departamento', 'municipio'),
                'direccion',
                'telefono'
            )
        }),
        ('Establecimiento de Salud', {
            'fields': ('centro_atencion',)
        }),
        ('Auditoría', {
            'fields': ('usuario_creacion', 'fecha_creacion', 'fecha_modificacion', 'activo'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    def nombre_completo_display(self, obj):
        return obj.nombre_completo
    nombre_completo_display.short_description = 'Nombre Completo'
    
    def edad_display(self, obj):
        return f"{obj.edad} años"
    edad_display.short_description = 'Edad'
    
    def cantidad_muestras(self, obj):
        count = obj.muestras.count()
        pos = obj.muestras.filter(resultado='POS').count()
        neg = obj.muestras.filter(resultado='NEG').count()
        
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 8px; border-radius: 3px; margin-right: 5px;">Total: {}</span>'
            '<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; margin-right: 5px;">POS: {}</span>'
            '<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 3px;">NEG: {}</span>',
            count, pos, neg
        )
    cantidad_muestras.short_description = 'Muestras'


# ==================== MUESTRA ====================

@admin.register(Muestra)
class MuestraAdmin(admin.ModelAdmin):
    list_display = (
        'numero_examen',
        'expediente_info',
        'centro_atencion',
        'fecha_examen',
        'resultado_badge',
        'parasitos_encontrados_resumido'
    )
    list_filter = (
        'resultado',
        'fecha_examen',
        'centro_atencion',
        'centro_atencion__region',
        'consistencia',
        'activo'
    )
    search_fields = (
        'numero_examen',
        'expediente__dni',
        'expediente__primer_nombre',
        'expediente__primer_apellido',
        'responsable_analisis'
    )
    ordering = ('-fecha_examen',)
    date_hierarchy = 'fecha_examen'
    
    fieldsets = (
        ('Información del Examen', {
            'fields': (
                'numero_examen',
                'fecha_examen',
                'responsable_analisis'
            )
        }),
        ('Paciente y Establecimiento', {
            'fields': (
                'expediente',
                'centro_atencion'
            )
        }),
        ('Examen Físico', {
            'fields': (
                'consistencia',
                'moco',
                'sangre_macroscopica'
            )
        }),
        ('Protozoos - Amebas', {
            'fields': (
                'entamoeba_histolytica',
                'entamoeba_coli',
                'entamoeba_hartmanni',
                'endolimax_nana',
                'iodamoeba_butschlii'
            ),
            'classes': ('collapse',)
        }),
        ('Protozoos - Flagelados y Ciliados', {
            'fields': (
                'giardia_intestinalis',
                'pentatrichomonas_hominis',
                'chilomastix_mesnili',
                'balantidium_coli'
            ),
            'classes': ('collapse',)
        }),
        ('Otros y Coccidios', {
            'fields': (
                'blastocystis_sp',
                'cystoisospora_belli',
                'cyclospora_cayetanensis',
                'cryptosporidium_spp'
            ),
            'classes': ('collapse',)
        }),
        ('Helmintos - Nematodos', {
            'fields': (
                'ascaris_lumbricoides',
                'ascaris_intensidad',
                'trichuris_trichiura',
                'necator_americanus',
                'strongyloides_stercoralis',
                'enterobius_vermicularis'
            ),
            'classes': ('collapse',)
        }),
        ('Helmintos - Cestodos', {
            'fields': (
                'taenia_spp',
                'hymenolepis_diminuta',
                'rodentolepis_nana'
            ),
            'classes': ('collapse',)
        }),
        ('Observaciones y Resultado', {
            'fields': (
                'observaciones',
                'resultado'
            )
        }),
        ('Auditoría', {
            'fields': (
                'usuario_creacion',
                'fecha_creacion',
                'fecha_modificacion',
                'activo'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('resultado', 'fecha_creacion', 'fecha_modificacion')
    
    def expediente_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.expediente.dni,
            obj.expediente.nombre_completo
        )
    expediente_info.short_description = 'Paciente'
    
    def resultado_badge(self, obj):
        if obj.resultado == 'POS':
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 5px 15px; border-radius: 3px; font-weight: bold;">POSITIVO</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 15px; border-radius: 3px; font-weight: bold;">NEGATIVO</span>'
            )
    resultado_badge.short_description = 'Resultado'
    
    def parasitos_encontrados_resumido(self, obj):
        parasitos = obj.get_parasitos_encontrados()
        if not parasitos:
            return format_html('<em style="color: #6c757d;">Sin parásitos</em>')
        
        # Mostrar solo los primeros 3 parásitos
        lista = list(parasitos.keys())[:3]
        texto = ', '.join(lista)
        
        if len(parasitos) > 3:
            texto += f' (+{len(parasitos) - 3} más)'
        
        return format_html('<span style="color: #dc3545; font-weight: bold;">{}</span>', texto)
    parasitos_encontrados_resumido.short_description = 'Parásitos'
    
    # Acciones personalizadas
    actions = ['marcar_como_inactivo', 'exportar_json']
    
    def marcar_como_inactivo(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} muestra(s) marcada(s) como inactiva(s).')
    marcar_como_inactivo.short_description = 'Marcar como inactivo'
    
    def exportar_json(self, request, queryset):
        # Aquí podrías implementar lógica de exportación
        self.message_user(request, f'Exportación de {queryset.count()} muestra(s) (función pendiente).')
    exportar_json.short_description = 'Exportar a JSON'


# ==================== PERSONALIZACIÓN DEL ADMIN SITE ====================

admin.site.site_header = "LNP - Sistema de Gestión"
admin.site.site_title = "LNP Admin"
admin.site.index_title = "Panel de Administración"