from django.urls import path
from .views import registro, iniciar_sesion, cerrar_sesion, mi_perfil

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('perfil/', mi_perfil, name='mi_perfil'),  # <--- nueva ruta
]
