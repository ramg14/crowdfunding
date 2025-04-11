# campanas/forms.py
from django import forms
from .models import Campana, Donacion

# campanas/forms.py

class CampanaForm(forms.ModelForm):
    class Meta:
        model = Campana
        fields = [
            'categoria',
            'nombre',
            'descripcion',
            'foto',
            'beneficiario',
            'monto_a_recaudar',
            'fecha_inicio',
            'fecha_cierre',
            'estado',
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduce el nombre de la campaña'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe tu campaña'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'beneficiario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del beneficiario'}),
            'monto_a_recaudar': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto a recaudar'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_cierre': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
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

from django import forms
from .models import Donacion

class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donacion
        fields = ['monto']  # Asegúrate de incluir 'monto' aquí
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el monto'
            }),
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto



