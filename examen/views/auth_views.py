from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from ..forms import LoginForm


@never_cache
@csrf_protect
def login_view(request):
    """Vista de login"""
    
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('redirect_to_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Autenticar usuario
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Login exitoso
                login(request, user)
                
                # Configurar sesión
                if not remember_me:
                    # Sesión expira al cerrar navegador
                    request.session.set_expiry(0)
                else:
                    # Sesión de 30 días
                    request.session.set_expiry(2592000)
                
                # Guardar datos del perfil en sesión
                if hasattr(user, 'profile'):
                    profile = user.profile
                    request.session['rol_nivel'] = profile.rol.nivel
                    request.session['rol_nombre'] = profile.rol.nombre
                    
                    # Guardar región o centro según el rol
                    if profile.rol.nivel == 'REG' and profile.region:
                        request.session['region_id'] = profile.region.id
                        request.session['region_nombre'] = profile.region.nombre
                    elif profile.rol.nivel == 'CAT' and profile.centro_atencion:
                        request.session['centro_id'] = profile.centro_atencion.id
                        request.session['centro_nombre'] = profile.centro_atencion.nombre
                        request.session['region_id'] = profile.centro_atencion.region.id
                
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                
                # Redirigir al dashboard
                next_url = request.GET.get('next', 'redirect_to_dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'Iniciar Sesión'
    }
    
    return render(request, 'auth/login.html', context)


@login_required
def logout_view(request):
    """Vista de logout"""
    username = request.user.username
    logout(request)
    messages.success(request, f'Hasta luego, {username}. Has cerrado sesión correctamente.')
    return redirect('login')


def redirect_to_dashboard(request):
    """Redirige al dashboard según el rol del usuario"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if hasattr(request.user, 'profile'):
        nivel = request.user.profile.rol.nivel
        
        if nivel == 'LNP':
            return redirect('dashboard_nacional')
        elif nivel == 'REG':
            return redirect('dashboard_regional')
        elif nivel == 'CAT':
            return redirect('dashboard_centro')
    
    # Por defecto
    return redirect('dashboard_centro')


@login_required
def dashboard_view(request):
    """Dashboard temporal (placeholder)"""
    context = {
        'title': 'Dashboard',
        'user': request.user
    }
    return render(request, 'dashboard/dashboard.html', context)