# campanas/urls.py
from django.urls import path, include
from . import views
from .views import registrar_donacion
from .views import stripe_webhook
from .views import pago_exitoso, pago_cancelado
from .views import dashboard 
urlpatterns = [
    path('', views.lista_campanas, name='lista_campanas'),
    path('campana/<int:id>/', views.detalle_campana, name='detalle_campana'),
    path('campana/crear/', views.crear_campana, name='crear_campana'),
    path('campana/editar/<int:id>/', views.editar_campana, name='editar_campana'),
    path('campana/eliminar/<int:id>/', views.eliminar_campana, name='eliminar_campana'),
    path('donar/<int:id>/', views.registrar_donacion, name='registrar_donacion'),
    path('donar/<int:id>/', registrar_donacion, name='registrar_donacion'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('pago/exito/', pago_exitoso, name='pago_exitoso'),
    path('pago/cancelado/', pago_cancelado, name='pago_cancelado'),
    path('usuarios/', include('usuarios.urls')),
    path('dashboard/', dashboard, name='dashboard'),
]
