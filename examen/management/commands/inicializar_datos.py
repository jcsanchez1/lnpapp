from django.core.management.base import BaseCommand
from examen.models import Region, CentroAtencion, Rol, Expediente
from django.contrib.auth.models import User
from datetime import date

class Command(BaseCommand):
    help = 'Inicializa los datos base del sistema LNP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando carga de datos...\n'))

        # ========== 1. CREAR REGIONES ==========
        self.stdout.write("📍 Creando regiones...")
        
        region1, created = Region.objects.get_or_create(
            numero_region=1,
            defaults={'nombre': 'Región Metropolitana del Distrito Central'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Región 1 creada'))
        else:
            self.stdout.write('   ⚠️  Región 1 ya existía')
        
        region2, created = Region.objects.get_or_create(
            numero_region=2,
            defaults={'nombre': 'Región del Valle de Sula'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Región 2 creada'))
        else:
            self.stdout.write('   ⚠️  Región 2 ya existía')

        # ========== 2. CREAR CENTROS DE ATENCIÓN ==========
        self.stdout.write("\n🏥 Creando centros de atención...")
        
        centro1, created = CentroAtencion.objects.get_or_create(
            codigo='HOSP-001',
            defaults={
                'nombre': 'Hospital Escuela',
                'direccion': 'Barrio La Granja, Tegucigalpa',
                'telefono': '2222-0000',
                'region': region1,
                'es_regional': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Hospital Escuela creado'))
        
        centro2, created = CentroAtencion.objects.get_or_create(
            codigo='CS-002',
            defaults={
                'nombre': 'Centro de Salud Kennedy',
                'direccion': 'Col. Kennedy, Tegucigalpa',
                'telefono': '2222-1111',
                'region': region1,
                'es_regional': False
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ CS Kennedy creado'))
        
        centro3, created = CentroAtencion.objects.get_or_create(
            codigo='HOSP-003',
            defaults={
                'nombre': 'Hospital Mario Catarino Rivas',
                'direccion': 'San Pedro Sula, Cortés',
                'telefono': '2550-0000',
                'region': region2,
                'es_regional': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Hospital MCR creado'))

        # ========== 3. CREAR ROLES ==========
        self.stdout.write("\n👥 Creando roles...")
        
        rol_lnp, created = Rol.objects.get_or_create(
            nivel='LNP',
            defaults={
                'nombre': 'Administrador LNP',
                'descripcion': 'Acceso total al sistema',
                'puede_crear_usuarios': True,
                'puede_ver_todas_regiones': True,
                'puede_generar_reportes_nacionales': True,
                'puede_editar_configuracion': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Rol LNP creado'))
        
        rol_reg, created = Rol.objects.get_or_create(
            nivel='REG',
            defaults={
                'nombre': 'Coordinador Regional',
                'descripcion': 'Acceso a su región asignada'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Rol REG creado'))
        
        rol_cat, created = Rol.objects.get_or_create(
            nivel='CAT',
            defaults={
                'nombre': 'Usuario Centro',
                'descripcion': 'Acceso solo a su centro de atención'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✅ Rol CAT creado'))

        # ========== 4. VERIFICAR SUPERUSUARIO ==========
        self.stdout.write("\n🔐 Verificando usuarios...")
        
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.ERROR('\n❌ ERROR: No hay superusuarios'))
            self.stdout.write(self.style.WARNING('⚠️  Ejecuta primero: python manage.py createsuperuser\n'))
            return
        
        usuario_admin = User.objects.filter(is_superuser=True).first()
        
        # Actualizar perfil
        if hasattr(usuario_admin, 'profile'):
            profile_admin = usuario_admin.profile
            profile_admin.rol = rol_lnp
            profile_admin.save()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Perfil configurado para: {usuario_admin.username}'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ El usuario no tiene perfil'))

        # ========== 5. CREAR EXPEDIENTE DE PRUEBA ==========
        self.stdout.write("\n📋 Creando expediente de prueba...")
        
        expediente, created = Expediente.objects.get_or_create(
            dni='0801-1990-12345',
            defaults={
                'primer_nombre': 'Juan',
                'segundo_nombre': 'Carlos',
                'primer_apellido': 'Pérez',
                'segundo_apellido': 'López',
                'sexo': 'M',
                'fecha_nacimiento': date(1990, 5, 15),
                'departamento': 'Francisco Morazán',
                'municipio': 'Tegucigalpa',
                'direccion': 'Col. Kennedy, Bloque A, Casa 123',
                'telefono': '9999-8888',
                'centro_atencion': centro1,
                'usuario_creacion': usuario_admin
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'   ✅ Expediente creado: {expediente.nombre_completo}'))
            self.stdout.write(f'      Edad: {expediente.edad} años')
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Expediente ya existía: {expediente.nombre_completo}'))

        # ========== RESUMEN FINAL ==========
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE DATOS EN EL SISTEMA:"))
        self.stdout.write("="*60)
        self.stdout.write(f"📍 Regiones Sanitarias:      {Region.objects.count()}")
        self.stdout.write(f"🏥 Centros de Atención:      {CentroAtencion.objects.count()}")
        self.stdout.write(f"👥 Roles:                    {Rol.objects.count()}")
        self.stdout.write(f"🔐 Usuarios:                 {User.objects.count()}")
        self.stdout.write(f"📋 Expedientes:              {Expediente.objects.count()}")
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS('✅ ¡Sistema inicializado correctamente!\n'))