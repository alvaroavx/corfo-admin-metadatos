import requests
from dspace_api.models import DspaceCollection
from django.conf import settings

# URL base del servidor y credenciales de autenticación
DSPACE_API_URL = settings.DSPACE_API_URL
DSPACE_USERNAME = settings.DSPACE_USERNAME
DSPACE_PASSWORD = settings.DSPACE_PASSWORD

def autenticar_dspace():
    """
    Autentica con la API de DSpace y retorna un token de sesión.
    """
    url = f"{DSPACE_API_URL}/authn/login"
    headers = {"Content-Type": "application/json"}
    data = {"email": DSPACE_USERNAME, "password": DSPACE_PASSWORD}
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.headers.get("Authorization")  # Retorna el token de sesión
    else:
        return None  # Error de autenticación
    
def crear_workspace_item(token, registro):
    """
    Crea un nuevo workspace item en una colección específica en DSpace.
    Retorna el ID del workspace si tiene éxito, o None si falla.
    """
    url = f"{DSPACE_API_URL}/submission/workspaceitems"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    payload = {
        "collection": f"{DSPACE_API_URL}/core/collections/{registro.coleccion.uuid}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        registro.estado_envio = 'workspace_creado'
        registro.save() 
        return response.json()["id"]  # Retorna el ID del workspace item
    else:
        return None  # Error al crear el workspace

def actualizar_metadata(token, workspace_id, registro):
    """
    Agrega los metadatos Dublin Core al workspace item en DSpace.
    """
    url = f"{DSPACE_API_URL}/submission/workspaceitems/{workspace_id}/metadata"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    metadata = [
        {"key": "dc.title", "value": registro.titulo},
        {"key": "dc.creator", "value": registro.autor},
        {"key": "dc.description", "value": registro.descripcion},
        {"key": "dc.date.issued", "value": str(registro.fecha_publicacion)},
    ]

    response = requests.put(url, json=metadata, headers=headers)

    if response.status_code == 200:
        registro.estado_envio = 'metadata_ingresada'
        registro.save()
        return response.status_code == 200  # True si se actualizaron correctamente
    else:
        return None  # Error al ingresar metadata

def subir_archivo(token, workspace_id, registro):
    """
    Sube un archivo adjunto al workspace item en DSpace.
    """
    if not registro.archivo:
        return False  # No hay archivo para subir

    url = f"{DSPACE_API_URL}/submission/workspaceitems/{workspace_id}/bitstreams"
    headers = {
        "Authorization": token
    }
    files = {
        "file": (registro.archivo.name, registro.archivo.open("rb"), "application/pdf")
    }
    params = {"name": registro.archivo.name, "description": "Archivo principal"}

    response = requests.post(url, files=files, headers=headers, params=params)

    if response.status_code == 201:
        registro.estado_envio = 'archivo_subido'
        registro.save()
        return response.status_code == 201  # True si el archivo se subió correctamente
    else:
        return None  # Error al ingresar metadata

def publicar_item(token, workspace_id, registro):
    """
    Publica el workspace item en DSpace, haciéndolo accesible en el repositorio.
    """
    url = f"{DSPACE_API_URL}/submission/workspaceitems/{workspace_id}"
    headers = {
        "Authorization": token
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        registro.estado_envio = 'publicado'
        registro.save()
        return response.status_code == 200 or response.status_code == 201
    else:
        return None  # Error al publicar
    
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
