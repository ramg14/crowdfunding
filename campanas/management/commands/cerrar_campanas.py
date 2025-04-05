# campanas/management/commands/cerrar_campanas.py
from django.core.management.base import BaseCommand
from datetime import date
from campanas.models import Campana

class Command(BaseCommand):
    help = 'Cierra las campañas cuya fecha_cierre ya ha pasado.'

    def handle(self, *args, **options):
        hoy = date.today()
        # Filtrar campañas abiertas cuya fecha_cierre sea menor que hoy
        campanas_vencidas = Campana.objects.filter(estado='abierta', fecha_cierre__lt=hoy)
        
        if not campanas_vencidas:
            self.stdout.write(self.style.SUCCESS('No hay campañas por cerrar.'))
            return
        
        for campana in campanas_vencidas:
            campana.estado = 'cerrada'
            campana.save()
            self.stdout.write(self.style.SUCCESS(f"Campaña '{campana.nombre}' cerrada automáticamente."))
