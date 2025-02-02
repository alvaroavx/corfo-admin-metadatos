# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('dspace_admin')

# Usar una cadena para evitar que Celery tenga que serializar el objeto de configuración
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas de todos los módulos registrados de Django app
app.autodiscover_tasks()
