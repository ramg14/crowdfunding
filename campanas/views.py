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


stripe.api_key = settings.STRIPE_SECRET_KEY

def registrar_donacion(request, id):
    # Obtenemos la campana
    campana = get_object_or_404(Campana, id=id)

    if request.method == 'POST':
        # 1. Capturamos el monto que ingreso el usuario
        monto_str = request.POST.get('monto', '0')
        try:
            monto = float(monto_str)
        except ValueError:
            monto = 0

        # 2. Crear la sesion de Stripe Checkout
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
            # Donde redirigir si el pago se completa o se cancela
            success_url=request.build_absolute_uri('/pago/exito/'),
            cancel_url=request.build_absolute_uri('/pago/cancelado/'),
            # Enviamos metadata para luego identificar la campana y el monto
            metadata={
                'campana_id': str(campana.id),
                'monto': str(monto),
            },
        )

        # 3. Redirigir al usuario a la pagina de Stripe Checkout
        return redirect(session.url, code=303)

    else:
        # GET: Mostramos el formulario
        return render(request, 'campanas/form_donacion.html', {
            'campana': campana
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

    

def handle_checkout_session(session):
    from decimal import Decimal
    from django.contrib.auth.models import User
    from .models import Campana, Donacion

    campana_id = session.get('metadata', {}).get('campana_id')
    monto_str = session.get('metadata', {}).get('monto', '0')
    user_id = session.get('metadata', {}).get('user_id')  # si lo mandaste

    if not campana_id:
        print("No campana_id en metadata")
        return

    try:
        campana = Campana.objects.get(id=campana_id)
    except Campana.DoesNotExist:
        print(f"La campana con id={campana_id} no existe.")
        return

    try:
        monto_pagado = Decimal(monto_str)
    except:
        monto_pagado = Decimal('0')

    # Recuperar el usuario si se envio user_id
    funder = None
    if user_id and user_id != 'anon':
        try:
            funder = User.objects.get(id=user_id)
        except User.DoesNotExist:
            funder = None

    # Crear la donacion
    Donacion.objects.create(
        campana=campana,
        funder=funder,  # si es obligatorio y funder es None => error
        monto=monto_pagado
    )

    # Actualizar el monto recaudado
    campana.monto_recaudado += monto_pagado
    campana.save()

    print(f"Donacion de {monto_pagado} creada para campana {campana.nombre}")


def pago_exitoso(request):
    # Renderiza una plantilla de exito
    return render(request, 'campanas/pago_exitoso.html')

def pago_cancelado(request):
    # Renderiza una plantilla de pago cancelado
    return render(request, 'campanas/pago_cancelado.html')
