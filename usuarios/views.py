# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm
from django.contrib.auth.decorators import login_required
from campanas.models import Donacion, Campana
from django.db.models import Sum


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Podemos iniciar sesion automaticamente
            login(request, user)
            return redirect('lista_campanas')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('lista_campanas')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('lista_campanas')


@login_required
def mi_perfil(request):
    usuario = request.user

    # Donaciones del usuario
    donaciones = Donacion.objects.filter(funder=usuario)

    # Campanas creadas por el usuario
    campanas = Campana.objects.filter(creador=usuario)

    return render(request, 'usuarios/perfil.html', {
        'donaciones': donaciones,
        'campanas': campanas,
    })

# usuarios/views.py



@login_required
def mis_campanas(request):
    # Obtiene las campañas creadas por el usuario logueado
    campanas = Campana.objects.filter(creador=request.user)
    return render(request, 'usuarios/mis_campanas.html', {'campanas': campanas})

@login_required
def mis_donaciones(request):
    # Obtiene las donaciones del usuario logueado
    donaciones = Donacion.objects.filter(funder=request.user)
    return render(request, 'usuarios/mis_donaciones.html', {'donaciones': donaciones})

# usuarios/views.py


@login_required
def mis_estadisticas(request):
    user = request.user

    # Número de campañas creadas por el usuario
    total_campanas_creadas = Campana.objects.filter(creador=user).count()

    # Número de donaciones que ha hecho el usuario
    total_donaciones_hechas = Donacion.objects.filter(funder=user).count()

    # Monto total donado por el usuario
    total_donado = Donacion.objects.filter(funder=user).aggregate(Sum('monto'))['monto__sum'] or 0

    # Monto total recaudado en sus campañas (si quieres mostrarlo)
    total_recaudado_campanas = Campana.objects.filter(creador=user).aggregate(Sum('monto_recaudado'))['monto_recaudado__sum'] or 0

    context = {
        'total_campanas_creadas': total_campanas_creadas,
        'total_donaciones_hechas': total_donaciones_hechas,
        'total_donado': total_donado,
        'total_recaudado_campanas': total_recaudado_campanas,
    }
    return render(request, 'usuarios/mis_estadisticas.html', context)
