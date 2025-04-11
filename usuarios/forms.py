# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

# usuarios/forms.py

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        label='Nombre'
    )
    last_name = forms.CharField(
        required=True,
        label='Apellido'
    )
    email = forms.EmailField(
        required=True,
        label='Email'
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si existe el campo password, lo ocultamos y quitamos su texto
        if 'password' in self.fields:
            self.fields['password'].help_text = ''  # Elimina el texto “No se ha establecido la clave”, etc.
            self.fields['password'].widget = forms.HiddenInput()
