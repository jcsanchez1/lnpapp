from examen.models import Region, CentroAtencion, Rol, Profile, Expediente
from django.contrib.auth.models import User
from datetime import date

# ========== 1. CREAR REGIONES ==========
print("Creando regiones...")

region1 = Region.objects.create(
    nombre='Región Metropolitana del Distrito Central',
    numero_region=1
)

region2 = Region.objects.create(
    nombre='Región del Valle de Sula',
    numero_region=2
)

print(f"✅ Regiones creadas: {Region.objects.count()}")

# ========== 2. CREAR CENTROS DE ATENCIÓN ==========
print("\nCreando centros de atención...")

centro1 = CentroAtencion.objects.create(
    nombre='Hospital Escuela',
    codigo='HOSP-001',
    direccion='Barrio La Granja, Tegucigalpa',
    telefono='2222-0000',
    region=region1,
    es_regional=True
)

centro2 = CentroAtencion.objects.create(
    nombre='Centro de Salud Kennedy',
    codigo='CS-002',
    direccion='Col. Kennedy, Tegucigalpa',
    telefono='2222-1111',
    region=region1,
    es_regional=False
)

centro3 = CentroAtencion.objects.create(
    nombre='Hospital Mario Catarino Rivas',
    codigo='HOSP-003',
    direccion='San Pedro Sula, Cortés',
    telefono='2550-0000',
    region=region2,
    es_regional=True
)

print(f"✅ Centros creados: {CentroAtencion.objects.count()}")

# ========== 3. CREAR ROLES ==========
print("\nCreando roles...")

rol_lnp = Rol.objects.create(
    nombre='Administrador LNP',
    nivel='LNP',
    descripcion='Acceso total al sistema',
    puede_crear_usuarios=True,
    puede_ver_todas_regiones=True,
    puede_generar_reportes_nacionales=True,
    puede_editar_configuracion=True
)

rol_reg = Rol.objects.create(
    nombre='Coordinador Regional',
    nivel='REG',
    descripcion='Acceso a su región asignada',
    puede_crear_usuarios=False,
    puede_ver_todas_regiones=False,
    puede_generar_reportes_nacionales=False,
    puede_editar_configuracion=False
)

rol_cat = Rol.objects.create(
    nombre='Usuario Centro',
    nivel='CAT',
    descripcion='Acceso solo a su centro de atención',
    puede_crear_usuarios=False,
    puede_ver_todas_regiones=False,
    puede_generar_reportes_nacionales=False,
    puede_editar_configuracion=False
)

print(f"✅ Roles creados: {Rol.objects.count()}")

# ========== 4. ACTUALIZAR PERFIL DEL SUPERUSUARIO ==========
print("\nConfigurando perfil del superusuario...")

# Obtener el superusuario que acabas de crear
usuario_admin = User.objects.get(username='admin')  # Cambia 'admin' por tu username

# El signal ya creó un Profile, solo lo actualizamos
profile_admin = usuario_admin.profile
profile_admin.rol = rol_lnp  # Asignar rol LNP (acceso total)
profile_admin.save()

print(f"✅ Perfil configurado para: {usuario_admin.username}")

# ========== 5. CREAR EXPEDIENTE DE PRUEBA ==========
print("\nCreando expediente de prueba...")

expediente_prueba = Expediente.objects.create(
    dni='0801-1990-12345',
    primer_nombre='Juan',
    segundo_nombre='Carlos',
    primer_apellido='Pérez',
    segundo_apellido='López',
    sexo='M',
    fecha_nacimiento=date(1990, 5, 15),
    departamento='Francisco Morazán',
    municipio='Tegucigalpa',
    direccion='Col. Kennedy, Bloque A, Casa 123',
    telefono='9999-8888',
    centro_atencion=centro1,
    usuario_creacion=usuario_admin
)

print(f"✅ Expediente creado: {expediente_prueba}")
print(f"   Nombre completo: {expediente_prueba.nombre_completo}")
print(f"   Edad: {expediente_prueba.edad} años")

# ========== RESUMEN ==========
print("\n" + "="*50)
print("RESUMEN DE DATOS CREADOS:")
print("="*50)
print(f"Regiones: {Region.objects.count()}")
print(f"Centros de Atención: {CentroAtencion.objects.count()}")
print(f"Roles: {Rol.objects.count()}")
print(f"Usuarios: {User.objects.count()}")
print(f"Expedientes: {Expediente.objects.count()}")
print("="*50)
print("✅ ¡Sistema inicializado correctamente!")