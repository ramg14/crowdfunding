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

        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_monto_a_recaudar(self):
        valor = self.cleaned_data.get('monto_a_recaudar')
        if valor is not None and valor <= 0:
            raise forms.ValidationError("El monto a recaudar debe ser mayor que cero.")
        return valor

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_cierre = cleaned_data.get('fecha_cierre')

        # Validar que la fecha de inicio no sea posterior a la de cierre
        if fecha_inicio and fecha_cierre:
            if fecha_inicio > fecha_cierre:
                raise forms.ValidationError(
                    "La fecha de inicio no puede ser posterior a la fecha de cierre."
                )    

class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donacion
        fields = ['monto']
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto



