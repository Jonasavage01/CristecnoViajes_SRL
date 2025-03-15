# Generated by Django 5.1.6 on 2025-03-13 23:21

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
            model_name='cliente',
            name='creado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clientes_creados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cliente',
            name='editado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clientes_editados', to=settings.AUTH_USER_MODEL, verbose_name='Último Editor'),
        ),
        migrations.AddField(
            model_name='documentocliente',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='crm.cliente', verbose_name='Cliente'),
        ),
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
        migrations.AddField(
            model_name='empresa',
            name='creado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='empresas_creadas', to=settings.AUTH_USER_MODEL, verbose_name='Creado por'),
        ),
        migrations.AddField(
            model_name='empresa',
            name='editado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='empresas_editadas', to=settings.AUTH_USER_MODEL, verbose_name='Último editor'),
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
            model_name='cliente',
            index=models.Index(fields=['cedula_pasaporte'], name='crm_cliente_cedula__286563_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['email'], name='crm_cliente_email_3bea01_idx'),
        ),
        migrations.AddIndex(
            model_name='documentocliente',
            index=models.Index(fields=['cliente', 'tipo'], name='crm_documen_cliente_e193c3_idx'),
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
        migrations.AddIndex(
            model_name='documentoempresa',
            index=models.Index(fields=['empresa', 'tipo'], name='crm_documen_empresa_deda89_idx'),
        ),
    ]
