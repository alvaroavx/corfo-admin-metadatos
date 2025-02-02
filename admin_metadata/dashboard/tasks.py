# metadata/tasks.py
from celery import shared_task
import requests
from dashboard.models import Register
from dspace_api.services import *

@shared_task
def autenticar_dspace_task(registro_id):
    # Aquí iría tu lógica de autenticación con DSpace
    registro = Register.objects.get(id=registro_id)
    token = autenticar_dspace()
    if token:
        return "Autenticado"
    else:
        return "Error de autenticación"

@shared_task
def crear_workspace_item_task(registro_id, token):
    # Crear el workspace en DSpace
    registro = Register.objects.get(id=registro_id)
    workspace_id = crear_workspace_item(token, registro)
    if workspace_id:
        return "Workspace creado"
    else:
        return "Error al crear el workspace"

@shared_task
def actualizar_metadata_task(registro_id, token, workspace_id):
    # Actualizar la metadata en DSpace
    registro = Register.objects.get(id=registro_id)
    success = actualizar_metadata(token, workspace_id, registro)
    if success:
        return "Metadata ingresada"
    else:
        return "Error al ingresar metadata"

@shared_task
def subir_archivo_task(registro_id, token, workspace_id):
    # Subir el archivo a DSpace
    registro = Register.objects.get(id=registro_id)
    success = subir_archivo(token, workspace_id, registro)
    if success:
        return "Archivo subido"
    else:
        return "Error al subir archivo"

@shared_task
def publicar_item_task(registro_id, token, workspace_id):
    # Publicar el item en DSpace
    registro = Register.objects.get(id=registro_id)
    success = publicar_item(token, workspace_id)
    if success:
        return "Publicado"
    else:
        return "Error al publicar"
