from django.core.management.base import BaseCommand
from examen.models import Region, Departamento

class Command(BaseCommand):
    help = 'Crea las 20 regiones sanitarias de Honduras (18 departamentales + 2 metropolitanas)'

    def handle(self, *args, **kwargs):
        self.stdout.write('🗺️  Creando 20 Regiones Sanitarias de Honduras...\n')
        
        # Obtener todos los departamentos
        departamentos = {d.codigo: d for d in Departamento.objects.all()}
        
        # === 18 REGIONES DEPARTAMENTALES (1-18) ===
        regiones_departamentales = [
            (1, 'Atlántida', '01'),
            (2, 'Colón', '02'),
            (3, 'Comayagua', '03'),
            (4, 'Copán', '04'),
            (5, 'Cortés', '05'),
            (6, 'Choluteca', '06'),
            (7, 'El Paraíso', '07'),
            (8, 'Francisco Morazán', '08'),
            (9, 'Gracias a Dios', '09'),
            (10, 'Intibucá', '10'),
            (11, 'Islas de la Bahía', '11'),
            (12, 'La Paz', '12'),
            (13, 'Lempira', '13'),
            (14, 'Ocotepeque', '14'),
            (15, 'Olancho', '15'),
            (16, 'Santa Bárbara', '16'),
            (17, 'Valle', '17'),
            (18, 'Yoro', '18'),
        ]
        
        creadas = 0
        
        for num, nombre, cod_depto in regiones_departamentales:
            depto = departamentos.get(cod_depto)
            
            if not depto:
                self.stdout.write(
                    self.style.ERROR(f'❌ Departamento {cod_depto} no encontrado para región {num}')
                )
                continue
            
            region, created = Region.objects.update_or_create(
                numero_region=num,
                defaults={
                    'nombre': nombre,
                    'es_metropolitana': False,
                    'departamento': depto,
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Región {num:2d} (Departamental): {nombre}')
                )
                creadas += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Región {num:2d} actualizada: {nombre}')
                )
        
        # === 2 REGIONES METROPOLITANAS (19-20) ===
        regiones_metropolitanas = [
            (19, 'Área Metropolitana de Tegucigalpa'),
            (20, 'Área Metropolitana de San Pedro Sula'),
        ]
        
        for num, nombre in regiones_metropolitanas:
            region, created = Region.objects.update_or_create(
                numero_region=num,
                defaults={
                    'nombre': nombre,
                    'es_metropolitana': True,
                    'departamento': None,  # Metropolitanas no tienen departamento
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Región {num:2d} (Metropolitana): {nombre}')
                )
                creadas += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Región {num:2d} actualizada: {nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 ¡Proceso completado!\n'
                f'   📍 {creadas} regiones nuevas creadas\n'
                f'   🏥 Total: 20 regiones sanitarias (18 departamentales + 2 metropolitanas)\n'
            )
        )