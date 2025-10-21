# examen/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from smart_selects.db_fields import ChainedForeignKey  # <-- IMPORTAR

# NECESITAS AGREGAR ESTOS DOS MODELOS:

# ==================== NUEVOS MODELOS: DEPARTAMENTO Y MUNICIPIO ====================

class Departamento(models.Model):
    """Departamentos de Honduras (18 total)"""
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Departamento"
    )
    codigo = models.CharField(
        max_length=2,
        unique=True,
        verbose_name="Código Administrativo",
        help_text="Código de 2 dígitos (01-18)"
    )
    extension_territorial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Extensión Territorial (km²)"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Municipio(models.Model):
    """Municipios de Honduras (298 total)"""
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Municipio"
    )
    codigo = models.CharField(
        max_length=4,
        unique=True,
        verbose_name="Código Administrativo",
        help_text="Código de 4 dígitos (XXYY)"
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='municipios',
        verbose_name="Departamento"
    )
    es_cabecera = models.BooleanField(
        default=False,
        verbose_name="¿Es Cabecera Departamental?",
        help_text="Marca si este municipio es la cabecera del departamento"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['departamento', 'codigo']
        unique_together = ('departamento', 'nombre')

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.departamento.nombre})"


# ==================== MODELOS BASE - GEOGRAFÍA ====================

class Region(models.Model):
    """Regiones sanitarias de Honduras (18 departamentales + 2 metropolitanas = 20 total)"""
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nombre de la Región"
    )
    numero_region = models.IntegerField(
        unique=True, 
        verbose_name="Número de Región"
    )
    
    # === NUEVO: Tipo de región ===
    es_metropolitana = models.BooleanField(
        default=False,
        verbose_name="¿Es Región Metropolitana?",
        help_text="Regiones 19 y 20 son metropolitanas (Tegucigalpa y San Pedro Sula)"
    )
    
    # === NUEVO: Relación con departamento (solo para regiones departamentales 1-18) ===
    departamento = models.ForeignKey(
        'Departamento',
        on_delete=models.PROTECT,
        related_name='regiones',
        null=True,
        blank=True,
        verbose_name="Departamento",
        help_text="Solo para regiones departamentales (1-18). Regiones metropolitanas no tienen."
    )
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Región Sanitaria'
        verbose_name_plural = 'Regiones Sanitarias'
        ordering = ['numero_region']

    def __str__(self):
        tipo = "Metropolitana" if self.es_metropolitana else "Departamental"
        return f"Región {self.numero_region}: {self.nombre} ({tipo})"
    
    def clean(self):
        """Validar que regiones departamentales tengan departamento"""
        from django.core.exceptions import ValidationError
        
        if not self.es_metropolitana and not self.departamento:
            raise ValidationError({
                'departamento': 'Regiones departamentales (1-18) deben tener un departamento asignado.'
            })
        
        if self.es_metropolitana and self.departamento:
            raise ValidationError({
                'departamento': 'Regiones metropolitanas (19-20) no deben tener departamento asignado.'
            })


class CentroAtencion(models.Model):
    """Establecimientos de Salud (Centros de Atención)"""
    nombre = models.CharField(
        max_length=200, 
        verbose_name="Nombre del Establecimiento"
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código",
        help_text="Código único del establecimiento"
    )
    direccion = models.TextField(verbose_name="Dirección")
    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name="Teléfono"
    )
    
    # Relación con región
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='centros_atencion',
        verbose_name="Región Sanitaria"
    )
    
    # Flag especial para centros regionales
    es_regional = models.BooleanField(
        default=False,
        verbose_name="¿Es Centro Regional?",
        help_text="Indica si este centro tiene responsabilidad regional"
    )


    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Centro de Atención'
        verbose_name_plural = 'Centros de Atención'
        ordering = ['region', 'nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    

# ==================== SISTEMA DE USUARIOS Y ROLES ====================

class Rol(models.Model):
    """Roles del sistema con 3 niveles de acceso"""
    NIVEL_CHOICES = [
        ('LNP', 'Laboratorio Nacional de Parasitología'),
        ('REG', 'Regional'),
        ('CAT', 'Centro de Atención'),
    ]
    
    nombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre del Rol"
    )
    nivel = models.CharField(
        max_length=3,
        choices=NIVEL_CHOICES,
        verbose_name="Nivel de Acceso"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    # Permisos específicos
    puede_crear_usuarios = models.BooleanField(
        default=False,
        verbose_name="¿Puede crear usuarios?"
    )
    puede_ver_todas_regiones = models.BooleanField(
        default=False,
        verbose_name="¿Puede ver todas las regiones?"
    )
    puede_generar_reportes_nacionales = models.BooleanField(
        default=False,
        verbose_name="¿Puede generar reportes nacionales?"
    )
    puede_editar_configuracion = models.BooleanField(
        default=False,
        verbose_name="¿Puede editar configuración del sistema?"
    )
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nivel', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_display()})"


class Profile(models.Model):
    """Perfil extendido del usuario con asignación geográfica"""
    
    # Relación uno a uno con User de Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuario"
    )
    
    # Rol asignado
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name="Rol"
    )
    
    # Región (para usuarios REG)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name="Región Asignada",
        help_text="Solo para usuarios REG (Regional)"
    )
    
    # Centro de Atención (ENCADENADO a región)
    centro_atencion = ChainedForeignKey(
        CentroAtencion,
        chained_field="region",  # Se filtra basado en este campo
        chained_model_field="region",  # Campo en CentroAtencion que conecta con Region
        show_all=False,  # No mostrar todos si no hay región seleccionada
        auto_choose=True,  # Auto-seleccionar si solo hay una opción
        sort=True,  # Ordenar alfabéticamente
        null=True,
        blank=True,
        verbose_name="Centro de Atención Asignado",
        help_text="Solo para usuarios CAT (Centro de Atención)"
    )
    
    # Información adicional
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Teléfono"
    )
    cargo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cargo"
    )
    
    # Estado y auditoría
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activo?"
    )
    ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Acceso"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Modificación"
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['user__username']
    
    def __str__(self):
        nombre_completo = self.user.get_full_name() or self.user.username
        return f"{nombre_completo} - {self.rol.nombre}"
    
    def clean(self):
        """
        Validar que la asignación geográfica sea consistente con el rol:
        - LNP: No debe tener región ni centro
        - REG: Debe tener región (sin centro)
        - CAT: Debe tener centro (sin región)
        """
        from django.core.exceptions import ValidationError
        
        if self.rol.nivel == 'LNP':
            if self.region or self.centro_atencion:
                raise ValidationError(
                    'Usuario LNP no debe tener asignación geográfica (región o centro).'
                )
        
        elif self.rol.nivel == 'REG':
            if not self.region:
                raise ValidationError(
                    'Usuario REG debe tener una región asignada.'
                )
            if self.centro_atencion:
                raise ValidationError(
                    'Usuario REG no debe tener centro de atención asignado.'
                )
        
        elif self.rol.nivel == 'CAT':
            if not self.centro_atencion:
                raise ValidationError(
                    'Usuario CAT debe tener un centro de atención asignado.'
                )
            # Para CAT, la región se obtiene del centro
            if self.centro_atencion:
                self.region = self.centro_atencion.region
    
    def save(self, *args, **kwargs):
        """Ejecutar validación antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)

# ==================== MODELO EXPEDIENTE ====================

class Expediente(models.Model):
    """
    Expediente del paciente - UNO por paciente.
    DNI es obligatorio y único para garantizar trazabilidad.
    """
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    # DNI OBLIGATORIO
    dni = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{4}-\d{5}$',
                message='El DNI debe tener el formato: 0801-1990-12345'
            )
        ],
        verbose_name="DNI",
        help_text="Formato: 0801-1990-12345"
    )
    
    # Nombres
    primer_nombre = models.CharField(max_length=50, verbose_name="Primer Nombre")
    segundo_nombre = models.CharField(max_length=50, blank=True, verbose_name="Segundo Nombre")
    primer_apellido = models.CharField(max_length=50, verbose_name="Primer Apellido")
    segundo_apellido = models.CharField(max_length=50, blank=True, verbose_name="Segundo Apellido")
    
    # Datos demográficos
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    
    # === UBICACIÓN - NUEVOS CAMPOS ===
    departamento = models.ForeignKey(
        'Departamento',
        on_delete=models.PROTECT,
        related_name='expedientes',
        verbose_name="Departamento",
        null=True,
        blank=True,
        db_column='departamento_id'  # Usa la columna que ya creamos
    )
    municipio = ChainedForeignKey(
        'Municipio',
        chained_field="departamento",
        chained_model_field="departamento",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        related_name='expedientes',
        verbose_name="Municipio",
        null=True,
        blank=True,
        db_column='municipio_id'  # Usa la columna que ya creamos
    )
    
    # Campos antiguos (solo lectura)
    departamento_old = models.CharField(
        max_length=100,
        verbose_name="Departamento (antiguo)",
        null=True,
        blank=True,
        editable=False,
        db_column='departamento_old'
    )
    municipio_old = models.CharField(
        max_length=100,
        verbose_name="Municipio (antiguo)",
        null=True,
        blank=True,
        editable=False,
        db_column='municipio_old'
    )
    
    direccion = models.TextField(verbose_name="Dirección Completa")
    telefono = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    
    # Centro de atención
    centro_atencion = models.ForeignKey(
        CentroAtencion,
        on_delete=models.PROTECT,
        related_name='expedientes',
        verbose_name="Establecimiento de Salud"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última Modificación")
    usuario_creacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='expedientes_creados',
        verbose_name="Usuario que Creó el Expediente"
    )
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")
    
    class Meta:
        verbose_name = 'Expediente'
        verbose_name_plural = 'Expedientes'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['centro_atencion', '-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.dni} - {self.nombre_completo}"
    
    @property
    def nombre_completo(self):
        nombres = [self.primer_nombre, self.segundo_nombre]
        apellidos = [self.primer_apellido, self.segundo_apellido]
        nombres_str = ' '.join(filter(None, nombres))
        apellidos_str = ' '.join(filter(None, apellidos))
        return f"{nombres_str} {apellidos_str}"
    
    @property
    def edad(self):
        from datetime import date
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        
        if self.fecha_nacimiento and self.fecha_nacimiento > date.today():
            raise ValidationError({
                'fecha_nacimiento': 'La fecha de nacimiento no puede ser futura.'
            })
        
        if self.telefono:
            import re
            patron = r'^(\d{4}-\d{4}|\d{8})$'
            if not re.match(patron, self.telefono):
                raise ValidationError({
                    'telefono': 'El teléfono debe tener formato: 9999-9999 o 99999999'
                })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# ==================== CHOICES PARA PARÁSITOS ====================

# Consistencia de la muestra
CONSISTENCIA_CHOICES = [
    ('FOR', 'Formada'),
    ('BLA', 'Blanda'),
    ('LIQ', 'Líquida/Diarreica'),
]

# Presencia de moco y sangre
PRESENCIA_CHOICES = [
    ('NO', 'No'),
    ('SI', 'Sí'),
]

MOCO_CHOICES = [
    ('N', 'No se observa'),
    ('E', 'Escaso'),
    ('M', 'Moderado'),
    ('A', 'Abundante'),
]

# Estadios de PROTOZOOS (Amebas y Flagelados)
ESTADIOS_PROTOZOO = [
    ('', 'No se observa'),
    ('T', 'Trofozoíto'),
    ('Q', 'Quiste'),
    ('TQ', 'Trofozoíto y Quiste'),
]

# Estadios de COCCIDIOS
ESTADIOS_COCCIDIO = [
    ('', 'No se observa'),
    ('O', 'Ooquiste'),
]

# Estadios de HELMINTOS - Nematodos
ESTADIOS_HELMINTO = [
    ('', 'No se observa'),
    ('H', 'Huevos'),
    ('L', 'Larva'),
    ('G', 'Gusano Adulto'),
]

# Estadios de CESTODOS (incluye proglótidos)
ESTADIOS_CESTODO = [
    ('', 'No se observa'),
    ('H', 'Huevos'),
    ('P', 'Proglótidos'),
    ('G', 'Gusano Adulto'),
]

# Intensidad de infección (método Kato-Katz)
INTENSIDAD_CHOICES = [
    ('', 'No aplica'),
    ('L', 'Leve'),
    ('M', 'Moderada'),
    ('S', 'Severa'),
]

# Resultado general
RESULTADO_CHOICES = [
    ('NEG', 'Negativo'),
    ('POS', 'Positivo'),
]

# ==================== MODELO SEMANA EPIDEMIOLÓGICA ====================

class SemanaEpidemiologica(models.Model):
    """
    Semanas epidemiológicas según ISO 8601.
    Permite agregar metadata y cachear estadísticas por semana.
    """
    año = models.IntegerField(
        verbose_name="Año"
    )
    semana = models.IntegerField(
        verbose_name="Número de Semana (1-53)",
        help_text="Semana según ISO 8601"
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio (Lunes)"
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha de Fin (Domingo)"
    )
    
    # === ESTADÍSTICAS CACHEADAS (se actualizan con signals) ===
    total_muestras = models.IntegerField(
        default=0,
        verbose_name="Total de Muestras"
    )
    total_positivas = models.IntegerField(
        default=0,
        verbose_name="Total Positivas"
    )
    total_negativas = models.IntegerField(
        default=0,
        verbose_name="Total Negativas"
    )
    
    # === ALERTAS Y METADATA ===
    alerta_activa = models.BooleanField(
        default=False,
        verbose_name="¿Alerta Epidemiológica Activa?"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas o Observaciones"
    )
    
    # === AUDITORÍA ===
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Semana Epidemiológica'
        verbose_name_plural = 'Semanas Epidemiológicas'
        ordering = ['-año', '-semana']
        unique_together = ('año', 'semana')
        indexes = [
            models.Index(fields=['año', 'semana']),
            models.Index(fields=['-año', '-semana']),
        ]
    
    def __str__(self):
        return f"Semana {self.semana}/{self.año}"
    
    @property
    def tasa_positividad(self):
        """Calcula el porcentaje de positividad"""
        if self.total_muestras > 0:
            return round((self.total_positivas / self.total_muestras) * 100, 2)
        return 0.0
    
    @classmethod
    def obtener_o_crear_desde_fecha(cls, fecha):
        """
        Obtiene o crea una SemanaEpidemiologica a partir de una fecha.
        Calcula automáticamente inicio y fin de semana.
        """
        from datetime import timedelta
        
        # Calcular semana según ISO 8601
        año, semana, dia_semana = fecha.isocalendar()
        
        # Calcular inicio (lunes) y fin (domingo)
        inicio_semana = fecha - timedelta(days=dia_semana - 1)
        fin_semana = inicio_semana + timedelta(days=6)
        
        # Obtener o crear
        semana_obj, created = cls.objects.get_or_create(
            año=año,
            semana=semana,
            defaults={
                'fecha_inicio': inicio_semana,
                'fecha_fin': fin_semana
            }
        )
        
        return semana_obj, created

# ==================== MODELO MUESTRA ====================

class Muestra(models.Model):
    """
    Muestra parasitológica individual.
    Cada muestra está vinculada a un expediente (paciente con DNI).
    El resultado (POS/NEG) se calcula automáticamente.
    """
    
    # === RELACIÓN CON EXPEDIENTE ===
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.PROTECT,
        related_name='muestras',
        verbose_name="Expediente del Paciente"
    )
    
    # === DATOS DEL EXAMEN ===
    numero_examen = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Examen",
        help_text="Código único del examen"
    )
    fecha_examen = models.DateField(
        verbose_name="Fecha del Examen"
    )

    
    # === SEMANA EPIDEMIOLÓGICA (HÍBRIDA) ===
    
    # Relación con modelo SemanaEpidemiologica
    semana_epidemiologica = models.ForeignKey(
        'SemanaEpidemiologica',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='muestras',
        verbose_name="Semana Epidemiológica"
    )
    
    # Campos denormalizados para queries rápidas (sin JOIN)
    semana_numero = models.IntegerField(
        editable=False,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número de Semana"
    )
    año_epidemiologico = models.IntegerField(
        editable=False,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Año Epidemiológico"
    )
    
    responsable_analisis = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Responsable del Análisis"
    )
    
    # === ESTABLECIMIENTO QUE ENVIÓ LA MUESTRA ===
    centro_atencion = models.ForeignKey(
        CentroAtencion,
        on_delete=models.PROTECT,
        related_name='muestras',
        verbose_name="Establecimiento de Salud"
    )
    
    # === EXAMEN FÍSICO (siempre se registra) ===
    consistencia = models.CharField(
        max_length=3,
        choices=CONSISTENCIA_CHOICES,
        verbose_name="Consistencia de la Muestra"
    )
    moco = models.CharField(
        max_length=1,
        choices=MOCO_CHOICES,
        default='N',
        verbose_name="Moco"
    )
    sangre_macroscopica = models.CharField(
        max_length=2,
        choices=PRESENCIA_CHOICES,
        default='NO',
        verbose_name="Sangre Macroscópica"
    )
    
    # === RESULTADO GENERAL (calculado automáticamente) ===
    resultado = models.CharField(
        max_length=3,
        choices=RESULTADO_CHOICES,
        default='NEG',
        verbose_name="Resultado",
        editable=False  # No se puede editar manualmente
    )
    
    # ========== PROTOZOOS - AMEBAS ==========
    entamoeba_histolytica = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Entamoeba histolytica"
    )
    entamoeba_coli = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Entamoeba coli"
    )
    entamoeba_hartmanni = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Entamoeba hartmanni"
    )
    endolimax_nana = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Endolimax nana"
    )
    iodamoeba_butschlii = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Iodamoeba bütschlii"
    )
    
    # ========== PROTOZOOS - FLAGELADOS ==========
    giardia_intestinalis = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Giardia intestinalis"
    )
    pentatrichomonas_hominis = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Pentatrichomonas hominis"
    )
    chilomastix_mesnili = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Chilomastix mesnili"
    )
    
    # ========== PROTOZOOS - CILIADOS ==========
    balantidium_coli = models.CharField(
        max_length=2,
        choices=ESTADIOS_PROTOZOO,
        blank=True,
        verbose_name="Balantidium coli"
    )
    
    # ========== OTROS (Blastocystis) ==========
    blastocystis_sp = models.CharField(
        max_length=1,
        choices=ESTADIOS_COCCIDIO,
        blank=True,
        verbose_name="Blastocystis sp"
    )
    
    # ========== COCCIDIOS ==========
    cystoisospora_belli = models.CharField(
        max_length=1,
        choices=ESTADIOS_COCCIDIO,
        blank=True,
        verbose_name="Cystoisospora belli"
    )
    cyclospora_cayetanensis = models.CharField(
        max_length=1,
        choices=ESTADIOS_COCCIDIO,
        blank=True,
        verbose_name="Cyclospora cayetanensis"
    )
    cryptosporidium_spp = models.CharField(
        max_length=1,
        choices=ESTADIOS_COCCIDIO,
        blank=True,
        verbose_name="Cryptosporidium spp"
    )
    
    # ========== HELMINTOS - NEMATODOS ==========
    ascaris_lumbricoides = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Ascaris lumbricoides"
    )
    ascaris_intensidad = models.CharField(
        max_length=1,
        choices=INTENSIDAD_CHOICES,
        blank=True,
        verbose_name="Intensidad de Infección (Kato-Katz)",
        help_text="Solo aplica para A. lumbricoides"
    )
    trichuris_trichiura = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Trichuris trichiura"
    )
    necator_americanus = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Necator americanus"
    )
    strongyloides_stercoralis = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Strongyloides stercoralis"
    )
    enterobius_vermicularis = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Enterobius vermicularis"
    )
    
    # ========== HELMINTOS - CESTODOS ==========
    taenia_spp = models.CharField(
        max_length=1,
        choices=ESTADIOS_CESTODO,
        blank=True,
        verbose_name="Taenia spp"
    )
    hymenolepis_diminuta = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Hymenolepis diminuta"
    )
    rodentolepis_nana = models.CharField(
        max_length=1,
        choices=ESTADIOS_HELMINTO,
        blank=True,
        verbose_name="Rodentolepis nana"
    )
    
    # === OBSERVACIONES ===
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # === AUDITORÍA ===
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Modificación"
    )
    usuario_creacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='muestras_creadas',
        verbose_name="Usuario que Creó la Muestra"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activo?"
    )
    
    class Meta:
        verbose_name = 'Muestra'
        verbose_name_plural = 'Muestras'
        ordering = ['-fecha_examen']
        indexes = [
            models.Index(fields=['numero_examen']),
            models.Index(fields=['expediente', '-fecha_examen']),
            models.Index(fields=['centro_atencion', '-fecha_examen']),
            models.Index(fields=['resultado', '-fecha_examen']),
        ]
    
    def __str__(self):
        return f"{self.numero_examen} - {self.expediente.dni} - {self.get_resultado_display()}"
    
    def _get_lista_parasitos(self):
        """Devuelve lista de todos los campos de parásitos con sus valores"""
        return [
            self.entamoeba_histolytica,
            self.entamoeba_coli,
            self.entamoeba_hartmanni,
            self.endolimax_nana,
            self.iodamoeba_butschlii,
            self.giardia_intestinalis,
            self.pentatrichomonas_hominis,
            self.chilomastix_mesnili,
            self.balantidium_coli,
            self.blastocystis_sp,
            self.cystoisospora_belli,
            self.cyclospora_cayetanensis,
            self.cryptosporidium_spp,
            self.ascaris_lumbricoides,
            self.trichuris_trichiura,
            self.necator_americanus,
            self.strongyloides_stercoralis,
            self.enterobius_vermicularis,
            self.taenia_spp,
            self.hymenolepis_diminuta,
            self.rodentolepis_nana,
        ]
    
    def calcular_resultado(self):
        """
        Calcula si la muestra es positiva o negativa.
        Positivo = al menos un parásito encontrado
        Negativo = ningún parásito encontrado
        """
        parasitos = self._get_lista_parasitos()
        # Si al menos un parásito tiene valor (no vacío) → Positivo
        tiene_parasitos = any(p for p in parasitos if p)
        return 'POS' if tiene_parasitos else 'NEG'
    
    def get_parasitos_encontrados(self):
        """
        Devuelve un diccionario con los parásitos encontrados y sus estadios.
        Útil para reportes y visualización.
        """
        encontrados = {}
        
        campos_parasitos = {
            'entamoeba_histolytica': 'Entamoeba histolytica',
            'entamoeba_coli': 'Entamoeba coli',
            'entamoeba_hartmanni': 'Entamoeba hartmanni',
            'endolimax_nana': 'Endolimax nana',
            'iodamoeba_butschlii': 'Iodamoeba bütschlii',
            'giardia_intestinalis': 'Giardia intestinalis',
            'pentatrichomonas_hominis': 'Pentatrichomonas hominis',
            'chilomastix_mesnili': 'Chilomastix mesnili',
            'balantidium_coli': 'Balantidium coli',
            'blastocystis_sp': 'Blastocystis sp',
            'cystoisospora_belli': 'Cystoisospora belli',
            'cyclospora_cayetanensis': 'Cyclospora cayetanensis',
            'cryptosporidium_spp': 'Cryptosporidium spp',
            'ascaris_lumbricoides': 'Ascaris lumbricoides',
            'trichuris_trichiura': 'Trichuris trichiura',
            'necator_americanus': 'Necator americanus',
            'strongyloides_stercoralis': 'Strongyloides stercoralis',
            'enterobius_vermicularis': 'Enterobius vermicularis',
            'taenia_spp': 'Taenia spp',
            'hymenolepis_diminuta': 'Hymenolepis diminuta',
            'rodentolepis_nana': 'Rodentolepis nana',
        }
        
        for campo, nombre in campos_parasitos.items():
            valor = getattr(self, campo)
            if valor:  # Si tiene algún valor
                # Obtener el display name del choice
                display_method = f'get_{campo}_display'
                if hasattr(self, display_method):
                    estadio = getattr(self, display_method)()
                else:
                    estadio = valor
                
                encontrados[nombre] = estadio
        
        return encontrados

#def get_semana_epidemiologica_display(self):
#    """Formato legible de semana epidemiológica"""
#    if self.semana_epidemiologica:
#        return str(self.semana_epidemiologica)
#    elif self.semana_numero and self.año_epidemiologico:
#        return f"Semana {self.semana_numero}/{self.año_epidemiologico}"
#    return "Sin calcular"

def save(self, *args, **kwargs):
    """Calcular resultado y asignar semana epidemiológica antes de guardar"""
    # Calcular resultado (POS/NEG)
    self.resultado = self.calcular_resultado()
    
    # Asignar semana epidemiológica
    if self.fecha_examen:
        # Obtener o crear SemanaEpidemiologica
        semana_obj, created = SemanaEpidemiologica.obtener_o_crear_desde_fecha(
            self.fecha_examen
        )
        
        # Asignar relación
        self.semana_epidemiologica = semana_obj
        
        # Campos denormalizados para queries rápidas
        self.semana_numero = semana_obj.semana
        self.año_epidemiologico = semana_obj.año
    
    super().save(*args, **kwargs)
    
    def to_export_json(self):
        """
        Genera un JSON completo con todos los datos de la muestra.
        Útil para exports, PowerBI, y reportes.
        """
        import json
        
        data = {
            "muestra_id": self.id,
            "numero_examen": self.numero_examen,
            "fecha_examen": self.fecha_examen.strftime('%Y-%m-%d'),
            "responsable": self.responsable_analisis,
            
            # Información del expediente
            "expediente": {
                "dni": self.expediente.dni,
                "nombre_completo": self.expediente.nombre_completo,
                "sexo": self.expediente.get_sexo_display(),
                "edad": self.expediente.edad,
                "departamento": self.expediente.departamento,
                "municipio": self.expediente.municipio,
            },
            
            # Información del centro y región
            "centro_atencion": {
                "codigo": self.centro_atencion.codigo,
                "nombre": self.centro_atencion.nombre,
                "es_regional": self.centro_atencion.es_regional,
                "region": {
                    "numero": self.centro_atencion.region.numero_region,
                    "nombre": self.centro_atencion.region.nombre
                }
            },
            
            # Características de la muestra
            "examen_fisico": {
                "consistencia": self.get_consistencia_display(),
                "moco": self.get_moco_display(),
                "sangre_macroscopica": self.get_sangre_macroscopica_display()
            },
            
            # Resultado general
            "resultado": {
                "codigo": self.resultado,
                "descripcion": self.get_resultado_display()
            },
            
            # Parásitos encontrados
            "parasitos_encontrados": self.get_parasitos_encontrados(),
            
            # Intensidad (si aplica)
            "kato_katz": {
                "intensidad": self.get_ascaris_intensidad_display() if self.ascaris_intensidad else None
            },
            
            # Observaciones
            "observaciones": self.observaciones
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)