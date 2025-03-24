# campanas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_campanas, name='lista_campanas'),
    path('campana/<int:id>/', views.detalle_campana, name='detalle_campana'),
    path('campana/crear/', views.crear_campana, name='crear_campana'),
    path('campana/editar/<int:id>/', views.editar_campana, name='editar_campana'),
    path('campana/eliminar/<int:id>/', views.eliminar_campana, name='eliminar_campana'),
    path('donar/<int:id>/', views.registrar_donacion, name='registrar_donacion'),
]