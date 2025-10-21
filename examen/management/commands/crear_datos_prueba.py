from django.core.management.base import BaseCommand
from examen.models import Expediente, Muestra, CentroAtencion
from django.contrib.auth.models import User
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Crea datos de prueba completos (expedientes y muestras con parásitos)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando creación de datos de prueba...\n'))
        
        # Obtener datos necesarios
        centro = CentroAtencion.objects.first()
        usuario = User.objects.first()
        
        if not centro or not usuario:
            self.stdout.write(self.style.ERROR('❌ Error: Primero ejecuta: python manage.py inicializar_datos'))
            return
        
        # === 1. CREAR EXPEDIENTES ===
        self.stdout.write('1️⃣ Creando expedientes...')
        
        nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Lucía', 'Miguel', 'Sofia', 'Jorge', 'Elena']
        apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Hernández', 'Díaz', 'Torres', 'Ramírez']
        
        expedientes = []
        for i in range(10):
            dni = f"0801-199{i}-{10000 + i:05d}"
            
            exp, created = Expediente.objects.get_or_create(
                dni=dni,
                defaults={
                    'primer_nombre': nombres[i],
                    'primer_apellido': apellidos[i],
                    'sexo': random.choice(['M', 'F']),
                    'fecha_nacimiento': date(1990 + i, random.randint(1, 12), random.randint(1, 28)),
                    'departamento': 'Francisco Morazán',
                    'municipio': 'Tegucigalpa',
                    'direccion': f'Col. Kennedy, Casa {i+1}',
                    'centro_atencion': centro,
                    'usuario_creacion': usuario
                }
            )
            expedientes.append(exp)
            if created:
                self.stdout.write(f'   ✅ {exp.dni} - {exp.nombre_completo}')
        
        self.stdout.write(self.style.SUCCESS(f'   Total expedientes: {len(expedientes)}\n'))
        
        # === 2. OBTENER ÚLTIMO NÚMERO DE MUESTRA ===
        ultimo_numero = 0
        if Muestra.objects.exists():
            ultima = Muestra.objects.order_by('-numero_examen').first()
            if ultima and ultima.numero_examen:
                try:
                    partes = ultima.numero_examen.split('-')
                    ultimo_numero = int(partes[-1])
                except:
                    ultimo_numero = Muestra.objects.count()
        
        # === 3. CREAR MUESTRAS ===
        self.stdout.write(f'2️⃣ Creando muestras (desde número {ultimo_numero + 1})...')
        
        muestras_creadas = 0
        positivas_creadas = 0
        fecha_actual = date.today()
        
        # Crear muestras para las últimas 12 semanas
        for semana_offset in range(12):
            fecha = fecha_actual - timedelta(weeks=semana_offset)
            
            # 3-5 muestras por semana
            for j in range(random.randint(3, 5)):
                ultimo_numero += 1
                numero = f"LNP-2025-{ultimo_numero:04d}"
                
                # 30% positivas
                es_positiva = random.random() < 0.3
                
                # Crear kwargs base
                kwargs = {
                    'expediente': random.choice(expedientes),
                    'numero_examen': numero,
                    'fecha_examen': fecha,
                    'responsable_analisis': 'Dra. María López',
                    'centro_atencion': centro,
                    'consistencia': random.choice(['FOR', 'BLA', 'LIQ']),
                    'moco': random.choice(['N', 'E', 'M', 'A']),
                    'sangre_macroscopica': random.choice(['NO', 'SI']),
                    'usuario_creacion': usuario
                }
                
                # Si es positiva, agregar parásitos
                if es_positiva:
                    kwargs['giardia_intestinalis'] = 'Q'
                    kwargs['ascaris_lumbricoides'] = 'H'
                    positivas_creadas += 1
                
                muestra = Muestra(**kwargs)
                # FORZAR resultado antes de guardar
                muestra.resultado = 'POS' if es_positiva else 'NEG'
                muestra.save()
                
                muestras_creadas += 1
                emoji = "🔴" if muestra.resultado == 'POS' else "🟢"
                self.stdout.write(f'   {emoji} {numero} - {muestra.resultado}')
        
        self.stdout.write(self.style.SUCCESS(f'\n   Muestras creadas: {muestras_creadas}'))
        self.stdout.write(self.style.SUCCESS(f'   Positivas: {positivas_creadas}'))
        self.stdout.write(self.style.SUCCESS(f'   Negativas: {muestras_creadas - positivas_creadas}\n'))
        
        # === 4. ESTADÍSTICAS FINALES ===
        total = Muestra.objects.count()
        pos = Muestra.objects.filter(resultado='POS').count()
        neg = Muestra.objects.filter(resultado='NEG').count()
        
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DEL SISTEMA'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Total muestras: {total}')
        self.stdout.write(f'Positivas: {pos} ({round(pos/total*100, 1) if total > 0 else 0}%)')
        self.stdout.write(f'Negativas: {neg} ({round(neg/total*100, 1) if total > 0 else 0}%)')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('\n✅ ¡Datos de prueba creados exitosamente!\n'))