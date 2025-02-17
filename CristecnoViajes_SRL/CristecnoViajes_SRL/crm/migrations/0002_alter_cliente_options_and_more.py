# Generated by Django 5.1.6 on 2025-02-13 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cliente',
            options={'ordering': ['-fecha_creacion'], 'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes'},
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='condicion_compra',
        ),
        migrations.AlterField(
            model_name='cliente',
            name='estado',
            field=models.CharField(choices=[('nuevo', 'Nuevo'), ('contactado', 'Contactado'), ('en_proceso', 'En Proceso'), ('convertido', 'Convertido')], default='nuevo', max_length=20, verbose_name='Estado del Lead'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='notas',
            field=models.TextField(blank=True, verbose_name='Notas Adicionales'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='ultima_actividad',
            field=models.DateTimeField(auto_now=True, verbose_name='Última Actividad'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['cedula_pasaporte'], name='crm_cliente_cedula__286563_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['email'], name='crm_cliente_email_3bea01_idx'),
        ),
    ]
