from django.core.management.base import BaseCommand
from examen.models import SemanaEpidemiologica
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Genera semanas epidemiológicas para un rango de años'

    def add_arguments(self, parser):
        parser.add_argument(
            '--año-inicio',
            type=int,
            default=2020,
            help='Año inicial (por defecto: 2020)'
        )
        parser.add_argument(
            '--año-fin',
            type=int,
            default=2025,
            help='Año final (por defecto: 2025)'
        )

    def handle(self, *args, **options):
        año_inicio = options['año_inicio']
        año_fin = options['año_fin']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n🗓️  Generando semanas epidemiológicas ({año_inicio}-{año_fin})...\n'
        ))
        
        creadas = 0
        existentes = 0
        
        for año in range(año_inicio, año_fin + 1):
            # Primera semana del año
            fecha = date(año, 1, 1)
            año_iso, semana_iso, dia = fecha.isocalendar()
            
            # Si el 1 de enero no es semana 1, avanzar al lunes de la semana 1
            if semana_iso != 1:
                dias_hasta_lunes = (7 - dia + 1) % 7
                fecha = fecha + timedelta(days=dias_hasta_lunes)
            
            # Determinar cuántas semanas tiene este año
            ultimo_dia = date(año, 12, 31)
            semanas_en_año = ultimo_dia.isocalendar()[1]
            
            # Si la última semana es 1, el año tiene 52 semanas
            if semanas_en_año == 1:
                semanas_en_año = 52
            
            for semana in range(1, semanas_en_año + 1):
                inicio_semana = fecha
                fin_semana = inicio_semana + timedelta(days=6)
                
                obj, created = SemanaEpidemiologica.objects.get_or_create(
                    año=año,
                    semana=semana,
                    defaults={
                        'fecha_inicio': inicio_semana,
                        'fecha_fin': fin_semana
                    }
                )
                
                if created:
                    creadas += 1
                    self.stdout.write(f'   ✅ Creada: {obj}')
                else:
                    existentes += 1
                
                fecha = fecha + timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f'\n📊 Resumen:'))
        self.stdout.write(f'   Semanas creadas: {creadas}')
        self.stdout.write(f'   Semanas existentes: {existentes}')
        self.stdout.write(f'   Total: {creadas + existentes}\n')
        self.stdout.write(self.style.SUCCESS('✅ ¡Proceso completado!\n'))