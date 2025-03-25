# usuarios/urls.py
from django.urls import path
from .views import registro, iniciar_sesion, cerrar_sesion

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
]
