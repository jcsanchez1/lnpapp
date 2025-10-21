from django.core.management.base import BaseCommand
from django.db import connection
from examen.models import Expediente, Departamento, Municipio

class Command(BaseCommand):
    help = 'Migra expedientes de CharField a ForeignKey para departamento y municipio'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Iniciando migración de expedientes...\n')
        
        # Mapeo de nombres alternativos de DEPARTAMENTOS
        mapeo_departamentos = {
            'francisco morazan': 'Francisco Morazán',
            'francisco morazán': 'Francisco Morazán',
            'atlantida': 'Atlántida',
            'atlántida': 'Atlántida',
            'colon': 'Colón',
            'colón': 'Colón',
            'el paraiso': 'El Paraíso',
            'el paraíso': 'El Paraíso',
            'cortes': 'Cortés',
            'cortés': 'Cortés',
            'copan': 'Copán',
            'copán': 'Copán',
            'santa barbara': 'Santa Bárbara',
            'santa bárbara': 'Santa Bárbara',
            'islas de la bahia': 'Islas de la Bahía',
            'islas de la bahía': 'Islas de la Bahía',
            'intibuca': 'Intibucá',
            'intibucá': 'Intibucá',
        }
        
        # Mapeo de nombres alternativos de MUNICIPIOS
        mapeo_municipios = {
            'tegucigalpa': 'Tegucigalpa D.C.',
            'san pedro sula': 'San Pedro Sula',
            'la ceiba': 'La Ceiba',
            'choloma': 'Choloma',
            'el progreso': 'El Progreso',
            'choluteca': 'Choluteca',
            'comayagua': 'Comayagua',
            'puerto cortes': 'Puerto Cortés',
            'puerto cortés': 'Puerto Cortés',
            'la lima': 'La Lima',
            'danli': 'Danlí',
            'danlí': 'Danlí',
            'siguatepeque': 'Siguatepeque',
            'juticalpa': 'Juticalpa',
            'tocoa': 'Tocoa',
            'tela': 'Tela',
            'santa rosa de copan': 'Santa Rosa de Copán',
            'santa rosa de copán': 'Santa Rosa de Copán',
            'villanueva': 'Villanueva',
            'la esperanza': 'La Esperanza',
            'nacaome': 'Nacaome',
            'yoro': 'Yoro',
        }
        
        # Cache de departamentos
        deptos = {d.nombre.lower(): d for d in Departamento.objects.all()}
        
        # Obtener datos directamente de la BD
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, departamento_old, municipio_old 
                FROM examen_expediente
                WHERE departamento_id IS NULL
            """)
            
            rows = cursor.fetchall()
            total = len(rows)
            actualizados = 0
            errores = []
            
            self.stdout.write(f'📊 Total de expedientes a migrar: {total}\n')
            
            for row in rows:
                exp_id, depto_texto, muni_texto = row
                
                if not depto_texto or not muni_texto:
                    errores.append({
                        'id': exp_id,
                        'error': 'Datos vacíos',
                        'depto': depto_texto,
                        'muni': muni_texto
                    })
                    continue
                
                # === NORMALIZAR DEPARTAMENTO ===
                depto_nombre = depto_texto.strip().lower()
                depto_nombre = mapeo_departamentos.get(depto_nombre, depto_nombre)
                
                # Buscar departamento
                depto_obj = deptos.get(depto_nombre.lower())
                
                if not depto_obj:
                    errores.append({
                        'id': exp_id,
                        'error': 'Departamento no encontrado',
                        'depto': depto_texto,
                        'muni': muni_texto
                    })
                    continue
                
                # === NORMALIZAR MUNICIPIO ===
                muni_nombre = muni_texto.strip().lower()
                muni_nombre_normalizado = mapeo_municipios.get(muni_nombre, muni_nombre)
                
                # Buscar municipio (intentar varias formas)
                muni_obj = None
                
                # Intento 1: Buscar con nombre normalizado (case-insensitive)
                try:
                    muni_obj = Municipio.objects.get(
                        departamento=depto_obj,
                        nombre__iexact=muni_nombre_normalizado
                    )
                except Municipio.DoesNotExist:
                    pass
                
                # Intento 2: Buscar con nombre original
                if not muni_obj:
                    try:
                        muni_obj = Municipio.objects.get(
                            departamento=depto_obj,
                            nombre__iexact=muni_texto.strip()
                        )
                    except Municipio.DoesNotExist:
                        pass
                
                # Intento 3: Buscar con LIKE (contiene)
                if not muni_obj:
                    try:
                        muni_obj = Municipio.objects.filter(
                            departamento=depto_obj,
                            nombre__icontains=muni_texto.strip()
                        ).first()
                    except:
                        pass
                
                # Si encontró el municipio, actualizar
                if muni_obj:
                    Expediente.objects.filter(id=exp_id).update(
                        departamento=depto_obj,
                        municipio=muni_obj
                    )
                    
                    actualizados += 1
                    
                    if actualizados % 5 == 0:
                        self.stdout.write(f'  ✅ Migrados: {actualizados}/{total}')
                else:
                    # No se encontró el municipio
                    errores.append({
                        'id': exp_id,
                        'error': 'Municipio no encontrado',
                        'depto': depto_texto,
                        'muni': muni_texto,
                        'depto_obj': depto_obj.nombre if depto_obj else 'N/A'
                    })
        
        # Resumen
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 ¡Migración completada!\n'
                f'   ✅ Expedientes migrados: {actualizados}\n'
                f'   ❌ Errores: {len(errores)}\n'
            )
        )
        
        if errores:
            self.stdout.write(self.style.WARNING('\n⚠️  Expedientes con errores:\n'))
            for err in errores[:20]:
                depto_info = err.get('depto_obj', err['depto'])
                self.stdout.write(
                    f"   ID {err['id']}: {err['error']} - "
                    f"{depto_info}/{err['muni']}"
                )
            
            if len(errores) > 20:
                self.stdout.write(
                    self.style.WARNING(f'\n   ... y {len(errores) - 20} errores más')
                )
            
            # Sugerencia: Listar municipios del departamento
            if errores:
                primer_error = errores[0]
                depto_nombre = primer_error.get('depto_obj', primer_error['depto'])
                try:
                    depto = Departamento.objects.get(nombre__iexact=depto_nombre)
                    munis = Municipio.objects.filter(departamento=depto).values_list('nombre', flat=True)
                    self.stdout.write(
                        self.style.WARNING(
                            f'\n💡 Municipios disponibles en {depto.nombre}:\n'
                            f'   {", ".join(list(munis)[:10])}'
                        )
                    )
                except:
                    pass