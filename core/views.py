from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from collections import defaultdict
from django.urls import reverse_lazy, reverse
from django.template.loader import render_to_string
import json
from django.core.paginator import Paginator
from .models import (
    Profile, Expediente, Muestra, 
    CentroAtencion, Region
)
from .forms import ExpedienteForm
# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    
    def form_valid(self, form):
        print("Form is valid")
        print(f"Username: {form.cleaned_data['username']}")
        try:
            response = super().form_valid(form)
            print(f"User authenticated: {self.request.user}")
            
            try:
                profile = Profile.objects.get(user=self.request.user)
                print(f"Profile found: {profile}")
                print(f"Centro: {profile.centro_atencion}")
                
                self.request.session['centro_id'] = profile.centro_atencion.id
                self.request.session['centro_nombre'] = profile.centro_atencion.nombre
                self.request.session['is_lnp'] = (profile.centro_atencion.nombre == 'LNP')
                print("Session data saved")
                
                return response
            except Profile.DoesNotExist:
                print("Profile not found")
                messages.error(self.request, "No se encontró el perfil del usuario")
                return redirect('login')
                
        except Exception as e:
            print(f"Error en login: {str(e)}")
            messages.error(self.request, "Error al iniciar sesión")
            return redirect('login')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_data(self, muestras):
        # Estadísticas de parásitos
        parasite_fields = [
            'Entamoeba_histolytica', 'Entamoeba_coli', 'Giardia_intestinalis',
            'Blastocystis_sp', 'Ascaris_lumbricoides', 'Trichuris_trichiura'
        ]
        
        parasite_counts = {
            field.replace('_', ' '): muestras.filter(
                **{f"{field}__in": ['T', 'Q', 'TQ', 'O', 'L', 'H', 'G', 'P']}
            ).count()
            for field in parasite_fields
        }

        # Datos mensuales
        last_6_months = timezone.now() - timedelta(days=180)
        monthly_data = defaultdict(lambda: {'total': 0, 'positive': 0})
        
        for muestra in muestras.filter(fecha__gte=last_6_months):
            month_key = muestra.fecha.strftime('%Y-%m')
            monthly_data[month_key]['total'] += 1
            if not muestra.No_se_observaron_parásitos:
                monthly_data[month_key]['positive'] += 1

        # Distribución por edad
        age_ranges = [(0, 5), (6, 12), (13, 18), (19, 30), (31, 50), (51, 100)]
        age_distribution = defaultdict(int)
        
        for muestra in muestras:
            for start, end in age_ranges:
                if start <= muestra.Edad <= end:
                    age_distribution[f"{start}-{end} años"] += 1
                    break

        return {
            'parasite_data': parasite_counts,
            'monthly_data': dict(monthly_data),
            'age_data': dict(age_distribution)
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_lnp = self.request.session.get('is_lnp', False)
        centro_id = self.request.session.get('centro_id')

        if is_lnp:
            muestras = Muestra.objects.all()
            expedientes = Expediente.objects.all()
            context.update({
                'regiones': Region.objects.all(),
                'centros': CentroAtencion.objects.all()
            })
        else:
            muestras = Muestra.objects.filter(
                expediente__profile__centro_atencion_id=centro_id
            )
            expedientes = Expediente.objects.filter(
                muestras__expediente__profile__centro_atencion_id=centro_id
            ).distinct()

        data = self.get_data(muestras)
        context.update({
            'total_expedientes': expedientes.count(),
            'total_muestras': muestras.count(),
            'muestras_hoy': muestras.filter(fecha=timezone.now().date()).count(),
            'muestras_positivas': muestras.filter(No_se_observaron_parásitos=False).count(),
            'parasite_data': json.dumps(data['parasite_data']),
            'monthly_data': json.dumps(data['monthly_data']),
            'age_data': json.dumps(data['age_data']),
            'muestras_recientes': muestras.order_by('-fecha')[:10]
        })

        return context

def dashboard_data(request):
    """API endpoint para filtrar datos del dashboard"""
    is_lnp = request.session.get('is_lnp', False)
    if not is_lnp:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    region_id = request.GET.get('region_id')
    centro_id = request.GET.get('centro_id')
    
    # Aplicar filtros
    filters = Q()
    if region_id:
        filters &= Q(expediente__profile__centro_atencion__region_id=region_id)
    if centro_id:
        filters &= Q(expediente__profile__centro_atencion_id=centro_id)
        
    muestras = Muestra.objects.filter(filters)
    
    view = DashboardView()
    data = view.get_data(muestras)
    
    return JsonResponse(data)

#===============================================================================
# views.py
class ExpedienteListView(LoginRequiredMixin, ListView):
    model = Expediente
    template_name = 'core/expediente_list.html'
    
    def get_queryset(self):
        if self.request.session.get('is_lnp'):
            return Expediente.objects.all()
        return Expediente.objects.filter(
            muestras__expediente__profile__centro_atencion_id=self.request.session.get('centro_id')
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente_form'] = ExpedienteForm()
        print("Context data loaded with form")
        return context

class MuestraListView(LoginRequiredMixin, ListView):
    model = Muestra
    template_name = 'core/muestra_list.html'
    
    def get_queryset(self):
        if self.request.session.get('is_lnp'):
            return Muestra.objects.all()
        return Muestra.objects.filter(
            expediente__profile__centro_atencion_id=self.request.session.get('centro_id')
        )

class RegionListView(LoginRequiredMixin, ListView):
   model = Region
   template_name = 'core/region_list.html'
   paginate_by = 5
   ordering = ['numero_region']

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       
       # Obtener la lista completa de regiones
       regiones = self.get_queryset()
       
       # Paginar los resultados
       paginator = Paginator(regiones, self.paginate_by)
       page = self.request.GET.get('page')
       context['regiones'] = paginator.get_page(page)
       
       # Agregar centros para cada región paginada
       context['centros_por_region'] = {
           region.id: region.centros_atencion.all() 
           for region in context['regiones']
       }
       
       return context
#===============================================================================
# views.py (adicional)
class ExpedienteDetailView(LoginRequiredMixin, DetailView):
    model = Expediente
    template_name = 'core/expediente_detail.html'

class MuestraDetailView(LoginRequiredMixin, DetailView):
    model = Muestra
    template_name = 'core/muestra_detail.html'

class ReportesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/reportes.html'
#===============================================================================
class RegionDetailView(LoginRequiredMixin, DetailView):
   model = Region
   template_name = 'core/region_detail.html'

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       region = self.get_object()
       
       # Obtener centros de atención de la región
       context['centros'] = region.centros_atencion.all()
       
       # Obtener muestras de la región
       muestras = Muestra.objects.filter(
           expediente__profile__centro_atencion__region=region
       ).select_related('Expediente', 'Expediente__profile__centro_atencion')
       
       context['muestras'] = muestras
       context['total_muestras'] = muestras.count()
       context['muestras_positivas'] = muestras.filter(No_se_observaron_parásitos=False).count()
       
       return context
#===============================================================================
class ExpedienteCreateView(LoginRequiredMixin, CreateView):
   model = Expediente
   fields = ['dni', 'nombre', 'apellido', 'sexo']
   template_name = 'core/expediente_form.html'
   success_url = reverse_lazy('expediente_list')

   def form_valid(self, form):
       response = super().form_valid(form)
       messages.success(self.request, 'Expediente creado exitosamente')
       if self.request.POST.get('crear_muestra') == 'si':
           return redirect('muestra_create', pk=self.object.pk)
       return response
#===============================================================================
class ExpedienteListDataView(LoginRequiredMixin, View):
   def get(self, request):
       # Parámetros de DataTables
       draw = int(request.GET.get('draw', 1))
       start = int(request.GET.get('start', 0))
       length = int(request.GET.get('length', 10))
       search_value = request.GET.get('search[value]', '')
       
       # Query base
       if request.session.get('is_lnp'):
           queryset = Expediente.objects.all()
       else:
           queryset = Expediente.objects.filter(
               muestras__expediente__profile__centro_atencion_id=request.session.get('centro_id')
           ).distinct()

       # Búsqueda
       if search_value:
           queryset = queryset.filter(
               Q(dni__icontains=search_value) |
               Q(nombre__icontains=search_value) |
               Q(apellido__icontains=search_value)
           )

       total = queryset.count()
       
       # Ordenamiento
       order_column = request.GET.get('order[0][column]', 0)
       order_dir = request.GET.get('order[0][dir]', 'asc')
       
       columns = ['dni', 'nombre', 'apellido', 'sexo']
       if order_column and int(order_column) < len(columns):
           column = columns[int(order_column)]
           if order_dir == 'desc':
               column = f'-{column}'
           queryset = queryset.order_by(column)

       # Paginación
       queryset = queryset[start:start + length]

       data = []
       for expediente in queryset:
           data.append({
               'dni': expediente.dni,
               'nombre': expediente.nombre,
               'apellido': expediente.apellido,
               'sexo': expediente.get_sexo_display(),
               'centro': expediente.profile.centro_atencion.nombre if hasattr(expediente, 'profile') else '',
               'acciones': render_to_string('core/expediente_actions.html', {'expediente': expediente})
           })

       return JsonResponse({
           'draw': draw,
           'recordsTotal': total,
           'recordsFiltered': total,
           'data': data,
       })

class MuestraCreateView(LoginRequiredMixin, CreateView):
   model = Muestra
   template_name = 'core/muestra_form.html'
   success_url = reverse_lazy('expediente_list')
   fields = ['Edad', 'consistencia', 'moco', 'sangre_macroscopica',
             'Entamoeba_histolytica', 'Entamoeba_coli', 'Entamoeba_hartmanni',
             'Endolimax_nana', 'Iodamoeba_bütschlii', 'Blastocystis_sp',
             'Giardia_intestinalis', 'Pentatrichomonas_hominis', 'Chilomastix_mesnili',
             'Balantidium_coli', 'Cystoisospora_belli', 'Cyclospora_cayetanensis',
             'Criptosporidium_spp', 'Strongyloides_stercoralis', 'Ascaris_lumbricoides',
             'Trichuris_trichiura', 'Necator_americanus', 'Enterobius_vermicularis',
             'Taenia_spp', 'Hymenolepis_diminuta', 'Rodentolepis_nana',
             'Intensidad_de_la_Infección_KATO_KATZ', 'No_se_observaron_parásitos']

   def form_valid(self, form):
       form.instance.Expediente_id = self.kwargs['pk']
       messages.success(self.request, 'Muestra creada exitosamente')
       return super().form_valid(form)
#===============================================================================
class MuestraListDataView(LoginRequiredMixin, View):
   def get(self, request):
       draw = int(request.GET.get('draw', 1))
       start = int(request.GET.get('start', 0))
       length = int(request.GET.get('length', 10))
       search_value = request.GET.get('search[value]', '')

       if request.session.get('is_lnp'):
           queryset = Muestra.objects.all()
       else:
           queryset = Muestra.objects.filter(
               expediente__profile__centro_atencion_id=request.session.get('centro_id')
           )

       if search_value:
           queryset = queryset.filter(
               Q(Expediente__dni__icontains=search_value) |
               Q(Expediente__nombre__icontains=search_value) |
               Q(Expediente__apellido__icontains=search_value)
           )

       total = queryset.count()
       
       columns = ['fecha', 'Expediente__dni', 'Expediente__nombre', 'Edad']
       order_column = request.GET.get('order[0][column]', 0)
       order_dir = request.GET.get('order[0][dir]', 'asc')
       
       if order_column and int(order_column) < len(columns):
           column = columns[int(order_column)]
           if order_dir == 'desc':
               column = f'-{column}'
           queryset = queryset.order_by(column)

       queryset = queryset[start:start + length]

       data = []
       for muestra in queryset:
           data.append({
               'fecha': muestra.fecha.strftime('%Y-%m-%d'),
               'dni': muestra.Expediente.dni,
               'paciente': f"{muestra.Expediente.nombre} {muestra.Expediente.apellido}",
               'edad': muestra.Edad,
               'centro': muestra.Expediente.profile.centro_atencion.nombre,
               'estado': 'Negativo' if muestra.No_se_observaron_parásitos else 'Positivo',
               'acciones': render_to_string('core/muestra_actions.html', {'muestra': muestra})
           })

       return JsonResponse({
           'draw': draw,
           'recordsTotal': total,
           'recordsFiltered': total,
           'data': data,
       })
#===============================================================================
class ExpedienteSearchView(LoginRequiredMixin, View):
    def get(self, request):
        dni = request.GET.get('dni')
        if not dni:
            return JsonResponse({'error': 'DNI requerido'})
            
        expedientes = Expediente.objects.filter(dni__icontains=dni)
        if not expedientes.exists():
            return render(request, 'core/expediente_search_results.html', {
                'no_results': True,
                'dni_buscado': dni
            })
            
        return render(request, 'core/expediente_search_results.html', {
            'expedientes': expedientes
        })
#===============================================================================
class ExpedienteAjaxCreateView(LoginRequiredMixin, View):
   def post(self, request):
       form = ExpedienteForm(request.POST)
       if form.is_valid():
           expediente = form.save()
           return JsonResponse({
               'success': True,
               'expediente_id': expediente.id,
               'redirect_url': reverse('muestra_create', args=[expediente.id])
           })
       return JsonResponse({'success': False, 'errors': form.errors})
