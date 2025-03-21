# Generated by Django 5.1.6 on 2025-03-20 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0005_reserva_comentarios_proveedor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='plan_type',
            field=models.CharField(choices=[('all_inclusive', 'All-Inclusive'), ('half_board', 'Half-Board')], default='all_inclusive', help_text='Tipo de plan del hotel', max_length=20),
        ),
    ]
