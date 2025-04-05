from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Campana(models.Model):
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='fotos/')
    beneficiario = models.CharField(max_length=100)
    monto_a_recaudar = models.DecimalField(max_digits=10, decimal_places=2)
    monto_recaudado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='abierta'
    )
    creador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='campanas_creadas',
        null=True,  # o False si deseas hacerlo obligatorio
        blank=True
    )

    def __str__(self):
        return self.nombre

    def clean(self):
        # Llamar a la validación base (opcional, pero recomendado)
        super().clean()
        if self.fecha_inicio and self.fecha_cierre and self.fecha_cierre < self.fecha_inicio:
            raise ValidationError("La fecha de cierre no puede ser anterior a la fecha de inicio.")
        if self.monto_a_recaudar <= 0:
            raise ValidationError("El monto a recaudar debe ser mayor que cero.")

class Donacion(models.Model):
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)
    funder = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.funder:
            return f"Donacion de {self.funder.username} a {self.campana}"
        else:
            return f"Donacion anonima a {self.campana}"
