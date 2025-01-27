from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from collections import defaultdict
import json
from .models import (
    Profile, Expediente, Muestra, 
    CentroAtencion, Region
)
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centros'] = CentroAtencion.objects.all()
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