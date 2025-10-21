from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Prepara la base de datos para migración de expedientes'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔧 Preparando migración de expedientes...\n')
        
        with connection.cursor() as cursor:
            # 1. Crear columnas temporales
            self.stdout.write('📝 Creando columnas temporales...')
            cursor.execute("""
                ALTER TABLE examen_expediente 
                ADD COLUMN departamento_old TEXT
            """)
            cursor.execute("""
                ALTER TABLE examen_expediente 
                ADD COLUMN municipio_old TEXT
            """)
            
            # 2. Copiar datos a columnas temporales
            self.stdout.write('📋 Copiando datos...')
            cursor.execute("""
                UPDATE examen_expediente 
                SET departamento_old = departamento,
                    municipio_old = municipio
            """)
            
            # 3. Crear columnas para FK (permitir NULL)
            self.stdout.write('🔗 Creando columnas para ForeignKey...')
            cursor.execute("""
                ALTER TABLE examen_expediente 
                ADD COLUMN departamento_id INTEGER
            """)
            cursor.execute("""
                ALTER TABLE examen_expediente 
                ADD COLUMN municipio_id INTEGER
            """)
            
            # Verificar
            cursor.execute("SELECT COUNT(*) FROM examen_expediente WHERE departamento_old IS NOT NULL")
            count = cursor.fetchone()[0]
            
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ ¡Preparación completada!\n'
                f'   📊 {count} expedientes con datos respaldados\n'
            )
        )