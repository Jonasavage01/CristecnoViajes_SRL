# Generated by Django 5.1.6 on 2025-03-20 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0004_reserva_total_tarifa'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='comentarios_proveedor',
            field=models.TextField(blank=True, help_text='Comentarios para el proveedor', null=True),
        ),
        migrations.AddField(
            model_name='reserva',
            name='comentarios_reserva',
            field=models.TextField(blank=True, help_text='Comentarios adicionales sobre la reserva', null=True),
        ),
        migrations.AddField(
            model_name='reserva',
            name='estado',
            field=models.CharField(default='pending', help_text='Estado de la reserva (e.g., pendiente, pagada, personalizado)', max_length=50),
        ),
        migrations.AddField(
            model_name='reserva',
            name='moneda',
            field=models.CharField(choices=[('USD', 'Dólares'), ('DOP', 'Pesos Dominicanos')], default='USD', help_text='Moneda en la que se expresa el total', max_length=3),
        ),
    ]
