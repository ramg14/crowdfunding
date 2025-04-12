# campanas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Campana, Categoria, Donacion
from .forms import CampanaForm, DonacionForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count



def lista_campanas(request):
    # Obtén todas las campañas
    campanas = Campana.objects.all().order_by('-fecha_inicio')  # Opcional, ordenar por fecha reciente primero
    
    # Filtro de búsqueda (por nombre)
    q = request.GET.get('q', '')
    if q:
        campanas = campanas.filter(nombre__icontains=q)
    
    # Filtro de categoría
    categoria_id = request.GET.get('categoria', '')
    if categoria_id:
        campanas = campanas.filter(categoria__id=categoria_id)
    
    # Filtro de estado
    estado = request.GET.get('estado', '')
    if estado in ['abierta', 'cerrada']:
        campanas = campanas.filter(estado=estado)
    
    # Calcular porcentaje ANTES de paginar
    for campana in campanas:
        if campana.monto_a_recaudar > 0:
            campana.porcentaje = (campana.monto_recaudado / campana.monto_a_recaudar) * 100
        else:
            campana.porcentaje = 0
    
    # Ahora sí, aplicar paginación
    paginator = Paginator(campanas, 9)
    page_number = request.GET.get('page')
    campanas_page = paginator.get_page(page_number)
    
    # Obtiene todas las categorías para el select
    categorias = Categoria.objects.all()
    
    return render(request, 'campanas/lista_campanas.html', {
        'campanas': campanas_page,
        'q': q,
        'categoria_id': categoria_id,
        'categorias': categorias,
        'estado': estado,
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


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from campanas.models import Campana, Donacion
from .forms import DonacionForm

@login_required
def registrar_donacion(request, id):

    print("==== EN registrar_donacion ====")  # <-- Depuración
    print("Usuario autenticado:", request.user, "ID:", request.user.id)

    campana = get_object_or_404(Campana, id=id)
    
    if request.method == 'POST':
        form = DonacionForm(request.POST)
        if form.is_valid():
            if campana.estado.lower() == 'abierta':
                donacion = form.save(commit=False)
                # Asignar la campaña a la donacion
                donacion.campana = campana
                # Asignar el usuario autenticado a la donacion
                donacion.funder = request.user
                donacion.save()

                # Actualizar el monto recaudado de la campaña
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


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def registrar_donacion(request, id):
    # Obtenemos la campaña
    campana = get_object_or_404(Campana, id=id)

    if request.method == 'POST':
        # Instanciamos el formulario con los datos POST
        form = DonacionForm(request.POST)
        if form.is_valid():
            # Obtenemos el monto validado del formulario
            monto = form.cleaned_data['monto']
            
            # Creamos la sesión de Stripe Checkout
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Donacion a {campana.nombre}",
                        },
                        'unit_amount': int(monto * 100),  # Convertir a centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/pago/exito/'),
                cancel_url=request.build_absolute_uri('/pago/cancelado/'),
                metadata={
                    'campana_id': str(campana.id),
                    'user_id': str(request.user.id),
                    'monto': str(monto),
                },
            )
            # Redirigimos al usuario a la página de Stripe Checkout
            return redirect(session.url, code=303)
    else:
        # Para el método GET, creamos un formulario vacío
        form = DonacionForm()
    
    # Renderizamos la plantilla, pasando tanto la campaña como el formulario al contexto
    return render(request, 'campanas/form_donacion.html', {
        'campana': campana,
        'form': form
    })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest("Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return HttpResponse(status=200)

    

from decimal import Decimal
from django.contrib.auth.models import User
from .models import Campana, Donacion

def handle_checkout_session(session):
    # Extraer metadatos
    campana_id = session.get('metadata', {}).get('campana_id')
    monto_str = session.get('metadata', {}).get('monto', '0')
    user_id = session.get('metadata', {}).get('user_id')  # Esto es opcional

    if not campana_id:
        print("No campana_id en metadata")
        return

    try:
        campana = Campana.objects.get(id=campana_id)
    except Campana.DoesNotExist:
        print(f"La campana con id {campana_id} no existe.")
        return

    try:
        monto_pagado = Decimal(monto_str)
    except Exception as e:
        print(f"Error al convertir el monto: {e}")
        monto_pagado = Decimal('0')

    # Determinar el usuario (funder)
    funder = None  # Por defecto, donación anónima
    if user_id and user_id != 'anon':
        try:
            funder = User.objects.get(id=user_id)
        except User.DoesNotExist:
            print("No se encontró el usuario con ese ID.")
            funder = None

    # Crear la donación
    donacion = Donacion.objects.create(
        campana=campana,
        funder=funder,
        monto=monto_pagado
    )

    # Actualizar el monto recaudado
    campana.monto_recaudado += monto_pagado
    campana.save()

    print(f"Donacion de {monto_pagado} creada para la campana {campana.nombre}")

def pago_exitoso(request):
    # Renderiza una plantilla de exito
    return render(request, 'campanas/pago_exitoso.html')

def pago_cancelado(request):
    # Renderiza una plantilla de pago cancelado
    return render(request, 'campanas/pago_cancelado.html')




# Opcional: aseguramos que solo el staff (administrador) pueda ver el dashboard.
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Consulta para el monto total de donaciones
    total_donaciones = Donacion.objects.aggregate(total=Sum('monto'))['total'] or 0

    # Consulta para obtener el número total de campañas
    total_campanas = Campana.objects.aggregate(total=Count('id'))['total'] or 0

    # Consulta para obtener el número total de donaciones
    total_donaciones_num = Donacion.objects.count()

    context = {
        'total_donaciones': total_donaciones,
        'total_campanas': total_campanas,
        'total_donaciones_num': total_donaciones_num,
    }
    return render(request, 'campanas/dashboard.html', context)

