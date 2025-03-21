# Generated by Django 5.1.6 on 2025-03-20 21:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0006_reserva_plan_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoReserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='documentos_reserva/%Y/%m/%d/')),
                ('subido_en', models.DateTimeField(auto_now_add=True)),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='reservas.reserva')),
            ],
        ),
    ]
