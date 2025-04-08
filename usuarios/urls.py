from django.urls import path
from .views import registro, iniciar_sesion, cerrar_sesion, mi_perfil
from .views import mis_campanas, mis_donaciones
urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('perfil/', mi_perfil, name='mi_perfil'),  # <--- nueva ruta
    path('mis-campanas/', mis_campanas, name='mis_campanas'),
    path('mis-donaciones/', mis_donaciones, name='mis_donaciones'),
]
