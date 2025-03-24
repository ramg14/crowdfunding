# campanas/forms.py
from django import forms
from .models import Campana, Donacion

class CampanaForm(forms.ModelForm):
    class Meta:
        model = Campana
        fields = [
            'categoria', 'nombre', 'descripcion', 'foto', 'beneficiario',
            'monto_a_recaudar', 'fecha_inicio', 'fecha_cierre', 'estado'
        ]

class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donacion
        fields = ['funder', 'monto']