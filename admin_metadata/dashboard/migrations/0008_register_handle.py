# Generated by Django 5.1.4 on 2025-04-10 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_register_item_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='handle',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Handle'),
        ),
    ]
