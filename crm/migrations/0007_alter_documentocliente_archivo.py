# Generated by Django 5.1.6 on 2025-02-20 23:45

import crm.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_notacliente_autor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentocliente',
            name='archivo',
            field=models.FileField(upload_to=crm.models.DocumentoCliente.archivo_upload_to),
        ),
    ]
