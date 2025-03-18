# Generated by Django 5.1.6 on 2025-03-18 02:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0002_initial'),
        ('reservas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='creado_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reserva',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.empresa'),
        ),
        migrations.AddField(
            model_name='habitacionreserva',
            name='reserva',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='habitaciones', to='reservas.reserva'),
        ),
        migrations.AddField(
            model_name='tipohabitacion',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.hotel'),
        ),
        migrations.AddField(
            model_name='habitacionreserva',
            name='tipo_habitacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.tipohabitacion'),
        ),
        migrations.AlterUniqueTogether(
            name='tipohabitacion',
            unique_together={('hotel', 'nombre')},
        ),
        migrations.AddConstraint(
            model_name='habitacionreserva',
            constraint=models.UniqueConstraint(fields=('reserva', 'tipo_habitacion'), name='unique_habitacion_por_reserva'),
        ),
    ]
