from django.urls import path
from .views import registro, iniciar_sesion, cerrar_sesion, mi_perfil
from .views import mis_campanas, mis_donaciones, mis_estadisticas, mis_datos
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('perfil/', mi_perfil, name='mi_perfil'),  # <--- nueva ruta
    path('mis-campanas/', mis_campanas, name='mis_campanas'),
    path('mis-donaciones/', mis_donaciones, name='mis_donaciones'),
    path('mis-estadisticas/', mis_estadisticas, name='mis_estadisticas'),
    path('mis-datos/', mis_datos, name='mis_datos'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
         template_name='usuarios/password_change.html'),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
         template_name='usuarios/password_change_done.html'),
         name='password_change_done'),
]
