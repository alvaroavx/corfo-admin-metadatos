# Generated by Django 5.1.4 on 2025-05-13 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_alter_register_sistema_origen'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='identificador',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Identificador'),
        ),
        migrations.AddField(
            model_name='register',
            name='proyecto_instrumento',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Proyecto Instrumento'),
        ),
    ]
