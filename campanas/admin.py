# campanas/admin.py
from django.contrib import admin
from .models import Categoria, Campana, Donacion

admin.site.register(Categoria)
admin.site.register(Campana)
admin.site.register(Donacion)