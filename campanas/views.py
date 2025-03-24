# campanas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Campana, Categoria, Donacion
from .forms import CampanaForm, DonacionForm

def lista_campanas(request):
    categorias = Categoria.objects.all()
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        campanas = Campana.objects.filter(categoria_id=categoria_id)
    else:
        campanas = Campana.objects.all()
    return render(request, 'campanas/lista_campanas.html', {
        'campanas': campanas,
        'categorias': categorias
    })

def detalle_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    return render(request, 'campanas/detalle_campana.html', {
        'campana': campana
    })

def crear_campana(request):
    if request.method == 'POST':
        form = CampanaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_campanas')
    else:
        form = CampanaForm()
    return render(request, 'campanas/form_campana.html', {
        'form': form,
        'accion': 'Crear'
    })

def editar_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    if request.method == 'POST':
        form = CampanaForm(request.POST, request.FILES, instance=campana)
        if form.is_valid():
            form.save()
            return redirect('detalle_campana', id=campana.id)
    else:
        form = CampanaForm(instance=campana)
    return render(request, 'campanas/form_campana.html', {
        'form': form,
        'accion': 'Editar'
    })

def eliminar_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    if request.method == 'POST':
        campana.delete()
        return redirect('lista_campanas')
    return render(request, 'campanas/confirmar_eliminar.html', {
        'campana': campana
    })

def registrar_donacion(request, id):
    campana = get_object_or_404(Campana, id=id)
    if request.method == 'POST':
        form = DonacionForm(request.POST)
        if form.is_valid():
            # Solo permitir donacion si la campana esta abierta
            if campana.estado.lower() == 'abierta':
                donacion = form.save(commit=False)
                donacion.campana = campana
                donacion.save()
                # Actualizar monto recaudado
                campana.monto_recaudado += donacion.monto
                campana.save()
            return redirect('detalle_campana', id=campana.id)
    else:
        form = DonacionForm()
    return render(request, 'campanas/form_donacion.html', {
        'form': form,
        'campana': campana
    })