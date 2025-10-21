from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from examen.models import Muestra, Expediente, SemanaEpidemiologica, CentroAtencion, Region, Departamento
from datetime import date, timedelta


@login_required
def dashboard_nacional(request):
    """Dashboard para usuarios LNP - Vista Nacional"""
    
    # Verificar permiso
    if request.user.profile.rol.nivel != 'LNP':
        return redirect('dashboard')
    
    # === ESTADÍSTICAS GENERALES ===
    total_muestras = Muestra.objects.count()
    total_positivas = Muestra.objects.filter(resultado='POS').count()
    total_negativas = Muestra.objects.filter(resultado='NEG').count()
    tasa_positividad = round((total_positivas / total_muestras * 100), 2) if total_muestras > 0 else 0
    
    # === ÚLTIMAS 100 MUESTRAS PARA TOP 5 PARÁSITOS ===
    ultimas_muestras = Muestra.objects.filter(resultado='POS').order_by('-fecha_examen')[:100]
    
    parasitos_count = {}
    for muestra in ultimas_muestras:
        for parasito, estadio in muestra.get_parasitos_encontrados().items():
            parasitos_count[parasito] = parasitos_count.get(parasito, 0) + 1
    
    # Top 5 parásitos
    top_parasitos = sorted(parasitos_count.items(), key=lambda x: x[1], reverse=True)[:5]
    top_5_nombres = [p[0] for p in top_parasitos] if top_parasitos else []
    
    # === MATRIZ REGIÓN X PARÁSITO (CORREGIDA) ===
    matriz_region_parasito = []
    totales_por_parasito = {parasito: 0 for parasito in top_5_nombres}
    
    for region in Region.objects.filter(activo=True).order_by('numero_region'):
        centros_ids = region.centros_atencion.values_list('id', flat=True)
        muestras_region = Muestra.objects.filter(
            resultado='POS',
            centro_atencion_id__in=centros_ids
        )
        
        fila = {
            'region': region,
            'parasitos': {}
        }
        
        # Contar cada parásito del top 5 en esta región
        for parasito in top_5_nombres:
            # Contar MUESTRAS ÚNICAS que tienen este parásito
            campo_modelo = {
                'Entamoeba histolytica': 'entamoeba_histolytica',
                'Entamoeba coli': 'entamoeba_coli',
                'Entamoeba hartmanni': 'entamoeba_hartmanni',
                'Endolimax nana': 'endolimax_nana',
                'Iodamoeba bütschlii': 'iodamoeba_butschlii',
                'Giardia intestinalis': 'giardia_intestinalis',
                'Pentatrichomonas hominis': 'pentatrichomonas_hominis',
                'Chilomastix mesnili': 'chilomastix_mesnili',
                'Balantidium coli': 'balantidium_coli',
                'Blastocystis sp': 'blastocystis_sp',
                'Cystoisospora belli': 'cystoisospora_belli',
                'Cyclospora cayetanensis': 'cyclospora_cayetanensis',
                'Cryptosporidium spp': 'cryptosporidium_spp',
                'Ascaris lumbricoides': 'ascaris_lumbricoides',
                'Trichuris trichiura': 'trichuris_trichiura',
                'Necator americanus': 'necator_americanus',
                'Strongyloides stercoralis': 'strongyloides_stercoralis',
                'Enterobius vermicularis': 'enterobius_vermicularis',
                'Taenia spp': 'taenia_spp',
                'Hymenolepis diminuta': 'hymenolepis_diminuta',
                'Rodentolepis nana': 'rodentolepis_nana',
            }.get(parasito)
            
            if campo_modelo:
                count = muestras_region.filter(
                    **{f'{campo_modelo}__isnull': False}
                ).exclude(
                    **{campo_modelo: ''}
                ).count()
                
                fila['parasitos'][parasito] = count
                totales_por_parasito[parasito] += count
        
        # Total de muestras ÚNICAS positivas en la región
        fila['total'] = muestras_region.count()
        matriz_region_parasito.append(fila)
    
    # === DATOS POR REGIÓN ===
    regiones_data = []
    for region in Region.objects.filter(activo=True).order_by('numero_region'):
        centros_ids = region.centros_atencion.values_list('id', flat=True)
        muestras_region = Muestra.objects.filter(centro_atencion_id__in=centros_ids)
        
        total = muestras_region.count()
        positivas = muestras_region.filter(resultado='POS').count()
        
        regiones_data.append({
            'region': region,
            'total_muestras': total,
            'total_positivas': positivas,
            'tasa_positividad': round((positivas / total * 100), 2) if total > 0 else 0
        })
    
    # === ÚLTIMAS 12 SEMANAS EPIDEMIOLÓGICAS ===
    semanas = SemanaEpidemiologica.objects.filter(
        total_muestras__gt=0
    ).order_by('-año', '-semana')[:12]
    
    # Datos para gráfico (orden cronológico)
    semanas_labels = []
    semanas_positivas = []
    semanas_negativas = []
    
    for semana in reversed(list(semanas)):
        semanas_labels.append(f"Sem {semana.semana}")
        semanas_positivas.append(semana.total_positivas)
        semanas_negativas.append(semana.total_negativas)
    
    # === TOP 10 CENTROS MÁS ACTIVOS ===
    top_centros = CentroAtencion.objects.annotate(
        num_muestras=Count('muestras')
    ).filter(num_muestras__gt=0).order_by('-num_muestras')[:10]
    
    # === ÚLTIMAS 10 MUESTRAS ===
    ultimas_muestras_list = Muestra.objects.select_related(
        'expediente', 'centro_atencion', 'semana_epidemiologica'
    ).order_by('-fecha_examen')[:10]
    
    # === NUEVA SECCIÓN: CONTEO COMPLETO DE 20 PARÁSITOS ===
    PARASITOS_COMPLETOS = {
        'Entamoeba histolytica': 'entamoeba_histolytica',
        'Entamoeba coli': 'entamoeba_coli',
        'Entamoeba hartmanni': 'entamoeba_hartmanni',
        'Endolimax nana': 'endolimax_nana',
        'Iodamoeba bütschlii': 'iodamoeba_butschlii',
        'Giardia intestinalis': 'giardia_intestinalis',
        'Pentatrichomonas hominis': 'pentatrichomonas_hominis',
        'Chilomastix mesnili': 'chilomastix_mesnili',
        'Balantidium coli': 'balantidium_coli',
        'Blastocystis sp': 'blastocystis_sp',
        'Cystoisospora belli': 'cystoisospora_belli',
        'Cyclospora cayetanensis': 'cyclospora_cayetanensis',
        'Cryptosporidium spp': 'cryptosporidium_spp',
        'Ascaris lumbricoides': 'ascaris_lumbricoides',
        'Trichuris trichiura': 'trichuris_trichiura',
        'Necator americanus': 'necator_americanus',
        'Strongyloides stercoralis': 'strongyloides_stercoralis',
        'Enterobius vermicularis': 'enterobius_vermicularis',
        'Taenia spp': 'taenia_spp',
        'Hymenolepis diminuta': 'hymenolepis_diminuta',
        'Rodentolepis nana': 'rodentolepis_nana',
    }
    
    # Contar todos los parásitos (muestras únicas)
    todos_parasitos = []
    muestras_positivas_all = Muestra.objects.filter(resultado='POS')
    
    for nombre_parasito, campo_modelo in PARASITOS_COMPLETOS.items():
        count = muestras_positivas_all.filter(
            **{f'{campo_modelo}__isnull': False}
        ).exclude(
            **{campo_modelo: ''}
        ).count()
        
        todos_parasitos.append({
            'nombre': nombre_parasito,
            'total': count,
            'porcentaje': round((count / total_positivas * 100), 2) if total_positivas > 0 else 0
        })
    
    # Ordenar por total (descendente)
    todos_parasitos = sorted(todos_parasitos, key=lambda x: x['total'], reverse=True)
    
    # === NUEVA SECCIÓN: DATOS PARA MAPA DE HONDURAS ===
    mapa_regiones_data = []
    for region in Region.objects.filter(activo=True).order_by('numero_region'):
        centros_ids = region.centros_atencion.values_list('id', flat=True)
        muestras_region = Muestra.objects.filter(centro_atencion_id__in=centros_ids)
        
        total = muestras_region.count()
        positivas = muestras_region.filter(resultado='POS').count()
        tasa = round((positivas / total * 100), 2) if total > 0 else 0
        
        # Clasificar intensidad para el mapa
        if tasa >= 15:
            intensidad = 'alta'
            color = '#dc3545'
        elif tasa >= 8:
            intensidad = 'media'
            color = '#ffc107'
        elif tasa > 0:
            intensidad = 'baja'
            color = '#28a745'
        else:
            intensidad = 'sin-datos'
            color = '#e9ecef'
        
        mapa_regiones_data.append({
            'numero': region.numero_region,
            'nombre': region.nombre,
            'total_muestras': total,
            'total_positivas': positivas,
            'tasa_positividad': tasa,
            'intensidad': intensidad,
            'color': color,
            'es_metropolitana': region.es_metropolitana
        })
    

    # === DATOS PARA MAPA INTERACTIVO POR DEPARTAMENTO ===
    mapa_departamentos_data = []
    
    for departamento in Departamento.objects.all().order_by('codigo'):
        # Obtener todas las regiones de este departamento
        regiones_depto = Region.objects.filter(departamento=departamento, activo=True)
        
        # Obtener todos los centros de estas regiones
        centros_ids = []
        for region in regiones_depto:
            centros_ids.extend(region.centros_atencion.values_list('id', flat=True))
        
        # Contar muestras del departamento
        muestras_depto = Muestra.objects.filter(centro_atencion_id__in=centros_ids)
        
        total = muestras_depto.count()
        positivas = muestras_depto.filter(resultado='POS').count()
        tasa = round((positivas / total * 100), 2) if total > 0 else 0
        
        # Top 3 parásitos del departamento
        top_parasitos_depto = []
        if positivas > 0:
            muestras_pos = muestras_depto.filter(resultado='POS')
            parasitos_depto = {}
            
            for nombre_parasito, campo_modelo in PARASITOS_COMPLETOS.items():
                count = muestras_pos.filter(
                    **{f'{campo_modelo}__isnull': False}
                ).exclude(
                    **{campo_modelo: ''}
                ).count()
                
                if count > 0:
                    parasitos_depto[nombre_parasito] = count
            
            # Top 3
            top_parasitos_depto = sorted(
                parasitos_depto.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
        
        mapa_departamentos_data.append({
            'codigo': departamento.codigo,
            'nombre': departamento.nombre,
            'total_muestras': total,
            'total_positivas': positivas,
            'tasa_positividad': tasa,
            'top_parasitos': top_parasitos_depto,
        })

    context = {
        'total_muestras': total_muestras,
        'total_positivas': total_positivas,
        'total_negativas': total_negativas,
        'tasa_positividad': tasa_positividad,
        'top_parasitos': top_parasitos,
        'top_5_nombres': top_5_nombres,
        'matriz_region_parasito': matriz_region_parasito,
        'totales_por_parasito': totales_por_parasito,
        'regiones_data': regiones_data,
        'semanas_labels': semanas_labels,
        'semanas_positivas': semanas_positivas,
        'semanas_negativas': semanas_negativas,
        'top_centros': top_centros,
        'ultimas_muestras': ultimas_muestras_list,
        
        # NUEVOS DATOS
        'todos_parasitos': todos_parasitos,  # Para tab de 20 parásitos
        'mapa_regiones_data': mapa_regiones_data,  # Para tab de mapa
        'mapa_departamentos_data': mapa_departamentos_data,  # NUEVO        
    }
    
    return render(request, 'dashboard/dashboard_nacional.html', context)

@login_required
def dashboard_regional(request):
    """Dashboard para usuarios REG - Vista Regional"""
    
    # Verificar permiso
    if request.user.profile.rol.nivel != 'REG':
        return redirect('dashboard')
    
    # Obtener región del usuario
    region = request.user.profile.region
    if not region:
        return redirect('dashboard')
    
    # IDs de centros de la región
    centros_ids = region.centros_atencion.values_list('id', flat=True)
    
    # === ESTADÍSTICAS DE LA REGIÓN ===
    muestras_region = Muestra.objects.filter(centro_atencion_id__in=centros_ids)
    
    total_muestras = muestras_region.count()
    total_positivas = muestras_region.filter(resultado='POS').count()
    total_negativas = muestras_region.filter(resultado='NEG').count()
    tasa_positividad = round((total_positivas / total_muestras * 100), 2) if total_muestras > 0 else 0
    
    # === TOP 5 PARÁSITOS DE LA REGIÓN ===
    ultimas_muestras = muestras_region.filter(resultado='POS').order_by('-fecha_examen')[:100]
    
    parasitos_count = {}
    for muestra in ultimas_muestras:
        for parasito, estadio in muestra.get_parasitos_encontrados().items():
            parasitos_count[parasito] = parasitos_count.get(parasito, 0) + 1
    
    top_parasitos = sorted(parasitos_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # === ÚLTIMAS 12 SEMANAS ===
    semanas = SemanaEpidemiologica.objects.filter(
        muestras__centro_atencion_id__in=centros_ids
    ).distinct().order_by('-año', '-semana')[:12]
    
    semanas_labels = []
    semanas_positivas = []
    semanas_negativas = []
    
    for semana in reversed(list(semanas)):
        muestras_semana = muestras_region.filter(semana_epidemiologica=semana)
        pos = muestras_semana.filter(resultado='POS').count()
        neg = muestras_semana.filter(resultado='NEG').count()
        
        semanas_labels.append(f"Sem {semana.semana}")
        semanas_positivas.append(pos)
        semanas_negativas.append(neg)
    
    # === CENTROS DE LA REGIÓN ===
    centros = CentroAtencion.objects.filter(
        id__in=centros_ids
    ).annotate(
        num_muestras=Count('muestras')
    ).order_by('-num_muestras')
    
    # === ÚLTIMAS 10 MUESTRAS DE LA REGIÓN ===
    ultimas_muestras_list = muestras_region.select_related(
        'expediente', 'centro_atencion', 'semana_epidemiologica'
    ).order_by('-fecha_examen')[:10]
    
    context = {
        'region': region,
        'total_muestras': total_muestras,
        'total_positivas': total_positivas,
        'total_negativas': total_negativas,
        'tasa_positividad': tasa_positividad,
        'top_parasitos': top_parasitos,
        'semanas_labels': semanas_labels,
        'semanas_positivas': semanas_positivas,
        'semanas_negativas': semanas_negativas,
        'centros': centros,
        'ultimas_muestras': ultimas_muestras_list,
    }
    
    return render(request, 'dashboard/dashboard_regional.html', context)


@login_required
def dashboard_centro(request):
    """Dashboard para usuarios CAT - Vista del Centro"""
    
    # Verificar permiso
    if request.user.profile.rol.nivel != 'CAT':
        return redirect('dashboard')
    
    # Obtener centro del usuario
    centro = request.user.profile.centro_atencion
    if not centro:
        return redirect('dashboard')
    
    # === ESTADÍSTICAS DEL CENTRO ===
    muestras_centro = Muestra.objects.filter(centro_atencion=centro)
    
    total_muestras = muestras_centro.count()
    total_positivas = muestras_centro.filter(resultado='POS').count()
    total_negativas = muestras_centro.filter(resultado='NEG').count()
    tasa_positividad = round((total_positivas / total_muestras * 100), 2) if total_muestras > 0 else 0
    
    # === TOP 5 PARÁSITOS DEL CENTRO ===
    ultimas_muestras = muestras_centro.filter(resultado='POS').order_by('-fecha_examen')[:50]
    
    parasitos_count = {}
    for muestra in ultimas_muestras:
        for parasito, estadio in muestra.get_parasitos_encontrados().items():
            parasitos_count[parasito] = parasitos_count.get(parasito, 0) + 1
    
    top_parasitos = sorted(parasitos_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # === ÚLTIMAS 12 SEMANAS ===
    semanas = SemanaEpidemiologica.objects.filter(
        muestras__centro_atencion=centro
    ).distinct().order_by('-año', '-semana')[:12]
    
    semanas_labels = []
    semanas_positivas = []
    semanas_negativas = []
    
    for semana in reversed(list(semanas)):
        muestras_semana = muestras_centro.filter(semana_epidemiologica=semana)
        pos = muestras_semana.filter(resultado='POS').count()
        neg = muestras_semana.filter(resultado='NEG').count()
        
        semanas_labels.append(f"Sem {semana.semana}")
        semanas_positivas.append(pos)
        semanas_negativas.append(neg)
    
    # === ÚLTIMAS 10 MUESTRAS DEL CENTRO ===
    ultimas_muestras_list = muestras_centro.select_related(
        'expediente', 'semana_epidemiologica'
    ).order_by('-fecha_examen')[:10]
    
    context = {
        'centro': centro,
        'total_muestras': total_muestras,
        'total_positivas': total_positivas,
        'total_negativas': total_negativas,
        'tasa_positividad': tasa_positividad,
        'top_parasitos': top_parasitos,
        'semanas_labels': semanas_labels,
        'semanas_positivas': semanas_positivas,
        'semanas_negativas': semanas_negativas,
        'ultimas_muestras': ultimas_muestras_list,
    }
    
    return render(request, 'dashboard/dashboard_centro.html', context)