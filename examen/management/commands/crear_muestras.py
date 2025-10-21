from examen.models import Expediente, Muestra, CentroAtencion, SemanaEpidemiologica
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

# Obtener datos necesarios
centro = CentroAtencion.objects.first()
usuario = User.objects.first()

if not centro:
    print("❌ Error: No hay centros de atención. Ejecuta primero: python manage.py inicializar_datos")
elif not usuario:
    print("❌ Error: No hay usuarios. Crea un superusuario primero.")
else:
    print("📋 Creando datos de prueba...")
    
    # === 1. CREAR EXPEDIENTES ===
    print("\n1️⃣ Creando expedientes...")
    
    expedientes = []
    nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Lucía', 'Miguel', 'Sofia', 'Jorge', 'Elena']
    apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Hernández', 'Díaz', 'Torres', 'Ramírez']
    
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
            print(f"   ✅ Expediente creado: {exp.dni} - {exp.nombre_completo}")
    
    # === 2. CREAR MUESTRAS ===
    print("\n2️⃣ Creando muestras...")
    
    # Lista de parásitos para variar
    parasitos_comunes = [
        ('giardia_intestinalis', 'Q'),
        ('ascaris_lumbricoides', 'H'),
        ('entamoeba_histolytica', 'T'),
        ('trichuris_trichiura', 'H'),
        ('blastocystis_sp', 'O'),
    ]
    
    muestras_creadas = 0
    
    # Crear muestras para las últimas 12 semanas
    fecha_actual = date.today()
    
    for semana_offset in range(12):
        fecha = fecha_actual - timedelta(weeks=semana_offset)
        
        # 3-5 muestras por semana
        for j in range(random.randint(3, 5)):
            expediente = random.choice(expedientes)
            
            # Número de examen único
            numero = f"LNP-2025-{muestras_creadas + 1:04d}"
            
            # Decidir si será positiva o negativa (70% negativas, 30% positivas)
            es_positiva = random.random() < 0.3
            
            # Datos base de la muestra
            muestra_data = {
                'expediente': expediente,
                'numero_examen': numero,
                'fecha_examen': fecha,
                'responsable_analisis': 'Dra. María López',
                'centro_atencion': centro,
                'consistencia': random.choice(['FOR', 'BLA', 'LIQ']),
                'moco': random.choice(['N', 'E', 'M', 'A']),
                'sangre_macroscopica': random.choice(['NO', 'SI']),
                'usuario_creacion': usuario
            }
            
            # Si es positiva, agregar 1-2 parásitos
            if es_positiva:
                parasito_seleccionado = random.choice(parasitos_comunes)
                campo, valor = parasito_seleccionado
                muestra_data[campo] = valor
                
                # 30% de probabilidad de tener un segundo parásito
                if random.random() < 0.3:
                    segundo_parasito = random.choice(parasitos_comunes)
                    campo2, valor2 = segundo_parasito
                    if campo2 != campo:  # No repetir el mismo parásito
                        muestra_data[campo2] = valor2
            
            # Crear muestra
            try:
                muestra = Muestra.objects.create(**muestra_data)
                muestras_creadas += 1
                
                resultado_emoji = "🔴" if muestra.resultado == 'POS' else "🟢"
                print(f"   {resultado_emoji} Muestra {numero} - {muestra.get_semana_epidemiologica_display()} - {muestra.get_resultado_display()}")
            except Exception as e:
                print(f"   ❌ Error creando muestra: {e}")
    
    print(f"\n✅ Proceso completado!")
    print(f"   📋 Expedientes: {len(expedientes)}")
    print(f"   🔬 Muestras creadas: {muestras_creadas}")
    
    # === 3. VERIFICAR ESTADÍSTICAS ===
    print("\n3️⃣ Verificando estadísticas...")
    
    total_muestras = Muestra.objects.count()
    total_positivas = Muestra.objects.filter(resultado='POS').count()
    total_negativas = Muestra.objects.filter(resultado='NEG').count()
    
    print(f"   Total muestras: {total_muestras}")
    print(f"   Positivas: {total_positivas} ({round(total_positivas/total_muestras*100, 1)}%)")
    print(f"   Negativas: {total_negativas} ({round(total_negativas/total_muestras*100, 1)}%)")
    
    # Ver semanas con muestras
    semanas_con_datos = SemanaEpidemiologica.objects.filter(total_muestras__gt=0).order_by('-año', '-semana')[:5]
    print(f"\n   📊 Top 5 semanas con más muestras:")
    for sem in semanas_con_datos:
        print(f"      {sem}: {sem.total_muestras} muestras ({sem.tasa_positividad}% positividad)")