import requests
import json
from django.conf import settings
from dspace_api.models import DspaceCollection
from dspace_api.client import DSpaceClient
from dashboard.models import Register, Metadata
from collections import defaultdict

# URL base del servidor y credenciales de autenticación
DSPACE_API_URL = settings.DSPACE_API_URL
DSPACE_USERNAME = settings.DSPACE_USERNAME
DSPACE_PASSWORD = settings.DSPACE_PASSWORD

def send_item_flow(id=None):
    """Flujo completo de envio del item a DSpace"""
    client = DSpaceClient()

    # 1: obtiene el csrf
    csrf = client.get_csrf()

    # 2: obtiene authentication token
    auth, csrf = client.authenticate(csrf)

    # Se extraen datos del registro y su coleccion
    try:
        register = Register.objects.get(id=id)
    except Register.DoesNotExist:
        return {"error": "Registro no encontrado"}
    collection = DspaceCollection.objects.get(handle=register.coleccion)
    
    # 3: Se crea un item nuevo
    item_payload = build_item_payload(register)
    item = client.create_item(item_payload, collection.uuid, csrf)

    # Se actualiza la informacion del Register
    register.item_uuid = item.get("uuid") if item.get("uuid") else ""
    register.handle = item.get("handle") if item.get("handle") else ""
    register.inArchive = item.get("inArchive") if item.get("inArchive") else ""
    register.discoverable = item.get("discoverable") if item.get("discoverable") else ""
    register.withdrawn = item.get("withdrawn") if item.get("withdrawn") else ""
    register.estado_envio = "item_creado"
    register.estado = "enviado"
    register.save()
    
    #print("item create response:\n", item)

    # 4: Subir archivo adjunto al item
    result_file = ""
    if register.archivo:
        result_file = client.upload_file_to_archived_item(register.item_uuid, register.archivo, csrf)
        register.estado_envio = "publicado"
        register.estado = "enviado"
        register.save()

    #print('file upload response', result_file)

    data = {
        'owning_collection': collection.uuid,
        'csrf': csrf,
        'auth': auth,
        'register': register.titulo + ' ' + register.autor + ' ' +  register.coleccion + ' ' +  register.estado,
        'workspaceitem_id': register.workspaceitem_id,
        'item_uuid': register.item_uuid,
        'item_payload': item_payload,
        'result_file': result_file
    }
    return data

def build_item_payload(register):
    """
    Construye dinámicamente el payload para crear un item en DSpace,
    a partir de un registro (modelo Register) y sus metadatos asociados.
    
    Retorna un diccionario con la estructura:
    {
      "name": <nombre del item>,
      "metadata": {
         "<full_key>": [
            {
              "value": <valor>,
              "language": "es_ES",
              "authority": null,
              "confidence": -1
            },
            ...
         ],
         ...
      },
      "inArchive": true,
      "discoverable": true,
      "withdrawn": false,
      "type": "item"
    }
    """
    payload = {}
    # Usamos el título del registro como "name". Si no existe, usamos un valor por defecto.
    payload["name"] = register.titulo if register.titulo else "Sin título"

    metadata = {}
    # Recorrer todos los metadatos asociados y agrupar según el campo compuesto.
    # Se asume que el campo completo se forma como: schema.element[.qualifier]
    for meta in register.metadata.all():
        field = meta.metadata_field
        key = f"{field.schema}.{field.element}" + (f".{field.qualifier}" if field.qualifier else "")
        if key not in metadata:
            metadata[key] = []
        entry = {
            "value": meta.text_value if meta.text_value is not None else None,
            "language": "es_ES",  # Forzamos el idioma a es_ES.
            "authority": None,     # Siempre null
            "confidence": -1       # Valor por defecto.
        }
        # Escapar saltos de línea en el valor (si es cadena) para evitar problemas en JSON.
        if entry["value"] is not None and isinstance(entry["value"], str):
            entry["value"] = entry["value"].replace("\r\n", "\n").replace("\n", "\\n")
        metadata[key].append(entry)

    payload["metadata"] = metadata
    payload["inArchive"] = True
    payload["discoverable"] = True
    payload["withdrawn"] = False
    payload["type"] = "item"

    # print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload

def build_dynamic_update_payload(register):
    """
    Paso 4. Construye de forma dinámica el payload de operaciones JSON Patch 
    a partir de los metadatos asociados a un registro.
    """
    # Agrupar los metadatos según el nombre compuesto: p.ej. "dc.title"
    groups = defaultdict(list)
    # Agrupar los metadatos según el campo compuesto, p. ej., "dc.title"
    for meta in register.metadata.all():
        field = meta.metadata_field
        full_key = f"{field.schema}.{field.element}" + (f".{field.qualifier}" if field.qualifier else "")
        groups[full_key].append(meta)

    operations = []
    # Para cada grupo se crea la operación
    for key, meta_list in groups.items():
        values = []
        for m in meta_list:
            # Si text_value es None, usamos None (para que aparezca como null en JSON)
            text_value = m.text_value if m.text_value is not None else None
            # Reemplazar los saltos de línea en el texto, si existe
            if text_value is not None:
                text_value = text_value.replace("\r\n", "\n").replace("\n", "\\n")
            entry = {
                "value": text_value,
                "language": m.text_lang if m.text_lang is not None else None,
                "authority": None,
                "confidence": -1
            }
            values.append(entry)
        op = {
            "op": "add",
            "path": f"/sections/traditionalpageone/{key}",
            "value": values
        }
        operations.append(op)
    return operations
    # Convertir el objeto Python a una cadena JSON; esto genera comillas dobles 
    # y convierte None en null
    #return json.dumps(operations, ensure_ascii=False)

def fetch_and_update_collections():
    """
    Obtiene las colecciones desde la API de DSpace y actualiza la base de datos local.
    """
    api_url = f"{DSPACE_API_URL}/core/collections?page=0&size=100"

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Lanza un error si la respuesta no es 200

        data = response.json()["_embedded"]["collections"]
        for collection in data:
            # Extrae los datos relevantes
            collection_id = collection["id"]
            uuid = collection["uuid"]
            name = collection["name"]
            handle = collection["handle"]
            uri = collection["metadata"]["dc.identifier.uri"][0]["value"]

            # Actualiza o crea la colección en la base de datos local
            DspaceCollection.objects.update_or_create(
                id=collection_id,
                defaults={
                    "uuid": uuid,
                    "name": name,
                    "handle": handle,
                    "uri": uri,
                },
            )

        return {"success": True, "message": f"Se actualizaron {len(data)} colecciones."}

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error al conectarse a la API: {str(e)}"}
    except KeyError as e:
        return {"success": False, "message": f"Error procesando la respuesta de la API: {str(e)}"}