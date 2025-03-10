# Generated by Django 5.1.6 on 2025-03-10 13:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='documentocliente',
            name='subido_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Subido por'),
        ),
        migrations.AddField(
            model_name='documentoempresa',
            name='subido_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Subido por'),
        ),
        migrations.AddIndex(
            model_name='empresa',
            index=models.Index(fields=['nombre_comercial'], name='crm_empresa_nombre__3917ed_idx'),
        ),
        migrations.AddIndex(
            model_name='empresa',
            index=models.Index(fields=['rnc'], name='crm_empresa_rnc_07998e_idx'),
        ),
        migrations.AddIndex(
            model_name='empresa',
            index=models.Index(fields=['direccion_electronica'], name='crm_empresa_direcci_26446d_idx'),
        ),
        migrations.AddIndex(
            model_name='empresa',
            index=models.Index(fields=['estado', 'fecha_registro'], name='crm_empresa_estado_acc481_idx'),
        ),
        migrations.AddField(
            model_name='documentoempresa',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_empresa', to='crm.empresa', verbose_name='Empresa'),
        ),
        migrations.AddField(
            model_name='notacliente',
            name='autor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notacliente',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notas_cliente', to='crm.cliente'),
        ),
        migrations.AddField(
            model_name='notaempresa',
            name='autor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notaempresa',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notas_empresa', to='crm.empresa'),
        ),
        migrations.AddIndex(
            model_name='documentocliente',
            index=models.Index(fields=['cliente', 'tipo'], name='crm_documen_cliente_e193c3_idx'),
        ),
        migrations.AddIndex(
            model_name='documentoempresa',
            index=models.Index(fields=['empresa', 'tipo'], name='crm_documen_empresa_deda89_idx'),
        ),
    ]
