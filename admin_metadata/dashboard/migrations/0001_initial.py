# Generated by Django 5.1.4 on 2025-01-21 20:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MetadataField',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('schema', models.CharField(choices=[('dc', 'Dublin Core'), ('cf', 'Corfo')], max_length=50, verbose_name='Esquema')),
                ('element', models.CharField(max_length=100, verbose_name='Elemento')),
                ('qualifier', models.CharField(blank=True, max_length=100, null=True, verbose_name='Calificador')),
            ],
        ),
        migrations.CreateModel(
            name='Register',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=255, verbose_name='Título')),
                ('autor', models.CharField(max_length=255, verbose_name='Autor')),
                ('sistema_origen', models.CharField(max_length=255, verbose_name='Sistema de origen')),
                ('fecha_carga', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de carga')),
                ('coleccion', models.CharField(max_length=255, verbose_name='Colección de destino')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], default='pendiente', max_length=10, verbose_name='Estado')),
            ],
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text_value', models.TextField(verbose_name='Valor del metadato')),
                ('text_lang', models.CharField(default='es_ES', max_length=10, verbose_name='Idioma')),
                ('metadata_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='dashboard.metadatafield', verbose_name='Campo de Metadata')),
                ('register', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='dashboard.register', verbose_name='Registro')),
            ],
        ),
    ]
