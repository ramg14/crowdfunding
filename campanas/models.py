# campanas/models.py
from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Campana(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='fotos/')
    beneficiario = models.CharField(max_length=100)
    monto_a_recaudar = models.DecimalField(max_digits=10, decimal_places=2)
    monto_recaudado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    estado = models.CharField(max_length=20)  # Ej: 'abierta' o 'cerrada'

    def __str__(self):
        return self.nombre

class Donacion(models.Model):
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)
    funder = models.ForeignKey(User, on_delete=models.CASCADE) 
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donacion de {self.funder.username} a {self.campana}"
