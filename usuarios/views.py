# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm
from django.contrib.auth.decorators import login_required
from campanas.models import Donacion, Campana

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