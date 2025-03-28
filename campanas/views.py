# campanas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Campana, Categoria, Donacion
from .forms import CampanaForm, DonacionForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden




def lista_campanas(request):
    from .models import Campana, Categoria  # si no lo tenias arriba

    categorias = Categoria.objects.all()
    q = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria')

    # 1. Obtenemos todas las campañas ordenadas
    campanas = Campana.objects.all().order_by('-fecha_inicio')

    # 2. Filtro por categoria
    if categoria_id:
        campanas = campanas.filter(categoria_id=categoria_id)

    # 3. Filtro por termino de busqueda (q)
    if q:
        campanas = campanas.filter(nombre__icontains=q)

    # 4. Crear el paginador: definimos cuantas campañas por pagina
    paginator = Paginator(campanas, 10)  # 10 campañas por pagina
    # 5. Obtenemos el numero de pagina desde la URL
    page_number = request.GET.get('page')
    # 6. Obtener la pagina actual (campanas_page)
    campanas_page = paginator.get_page(page_number)

    return render(request, 'campanas/lista_campanas.html', {
        'campanas': campanas_page,  # Enviamos la pagina actual
        'categorias': categorias,
        'q': q,
        'categoria_id': categoria_id,
    })

def detalle_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    return render(request, 'campanas/detalle_campana.html', {
        'campana': campana
    })

@login_required
def crear_campana(request):
    if request.method == 'POST':
        form = CampanaForm(request.POST, request.FILES)
        if form.is_valid():
            # Usamos commit=False para asignar manualmente el creador
            campana = form.save(commit=False)
            campana.creador = request.user  # Asignar el usuario logueado
            campana.save()
            return redirect('lista_campanas')
    else:
        form = CampanaForm()
    return render(request, 'campanas/form_campana.html', {
        'form': form,
        'accion': 'Crear'
    })


@login_required
def editar_campana(request, id):
    campana = get_object_or_404(Campana, id=id)

    # Comprobamos si el usuario NO es el creador y NO es staff
    if campana.creador != request.user and not request.user.is_staff:
        # Podrias mostrar un mensaje de error o redirigir
        return HttpResponseForbidden("No tienes permiso para editar esta campana.")

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


@login_required
def eliminar_campana(request, id):
    campana = get_object_or_404(Campana, id=id)

    # Comprobamos si el usuario NO es el creador y NO es staff
    if campana.creador != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para eliminar esta campana.")

    if request.method == 'POST':
        campana.delete()
        return redirect('lista_campanas')
    return render(request, 'campanas/confirmar_eliminar.html', {
        'campana': campana
    })


@login_required
def registrar_donacion(request, id):
    campana = get_object_or_404(Campana, id=id)
    if request.method == 'POST':
        form = DonacionForm(request.POST)
        if form.is_valid():
            if campana.estado.lower() == 'abierta':
                donacion = form.save(commit=False)
                donacion.campana = campana
                
                donacion.funder = request.user
                donacion.save()

                campana.monto_recaudado += donacion.monto
                campana.save()
            return redirect('detalle_campana', id=campana.id)
    else:
        form = DonacionForm()
    return render(request, 'campanas/form_donacion.html', {
        'form': form,
        'campana': campana
    })

# campanas/views.py
def detalle_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    if campana.monto_a_recaudar > 0:
        porcentaje = (campana.monto_recaudado / campana.monto_a_recaudar) * 100
    else:
        porcentaje = 0
    return render(request, 'campanas/detalle_campana.html', {
        'campana': campana,
        'porcentaje': porcentaje,
    })
