import requests
import json
from dspace_api.models import DspaceCollection
from django.conf import settings

# URL base del servidor y credenciales de autenticación
DSPACE_API_URL = settings.DSPACE_API_URL
DSPACE_USERNAME = settings.DSPACE_USERNAME
DSPACE_PASSWORD = settings.DSPACE_PASSWORD

class DSpaceClient:
    def __init__(self):
        self.base_url = DSPACE_API_URL
        self.session = requests.Session()
        self.token = None
        self.csrf_token = None
        self.cookies = None

    def get_csrf(self):
        """
            Paso 1. 
            Obtiene CSRF a traves de la API status
        """
        url = f"{self.base_url}/authn/status"
        response = requests.get(url)
        # Extraer la cookie DSPACE-XSRF-COOKIE
        self.csrf_token = response.cookies.get("DSPACE-XSRF-COOKIE")
        return self.csrf_token

    def authenticate(self, csrf):
        self.csrf_token = csrf
        """
            Paso 2. 
            Autentica el usuario en DSpace y obtiene el token de sesión y CSRF.
        """
        url = f"{self.base_url}/authn/login"
        credentials = {
            "user": DSPACE_USERNAME,
            "password": DSPACE_PASSWORD
        }
        headers = {
            "X-XSRF-TOKEN": csrf,  # Agregar el CSRF token al encabezado
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.cookies = {
            "DSPACE-XSRF-COOKIE": csrf  # Agregar la cookie CSRF
        }
        response = self.session.post(url, data=credentials, headers=headers, cookies=self.cookies)

        print("Respuesta de autenticación:", response.status_code, response.text)  # Mostrar en consola

        if response.status_code == 200:
            self.token = response.headers.get("Authorization")  # Bearer token
            self.csrf_token = response.headers.get("DSPACE-XSRF-TOKEN")  # CSRF token
            self.cookies = response.cookies.get_dict()
            #print("CSRF dentro de Auth: ", self.csrf_token)
            return self.token, self.csrf_token
        else:
            return False
        
    def create_item(self, payload, owning_collection, csrf):
        """ 
            Paso 3. Crea un item en DSpace usando la API REST.
            Parámetros:
            - payload: Diccionario con la estructura del item, por ejemplo:
                {
                    "name": "Test Item",
                    "metadata": { ... },
                    "inArchive": true,
                    "discoverable": true,
                    "withdrawn": false,
                    "type": "item"
                }
            - owning_collection: String con el UUID de la colección destino.
            Retorna:
            - Si la llamada es exitosa (status 200 o 201), el JSON de respuesta.
            - En caso contrario, un diccionario con el error y el status code.
            Se asume que self.csrf_token, self.token y self.cookies están configurados.
        """
        # Construir la URL con el parámetro owningCollection
        url = f"{self.base_url}/core/items?owningCollection={owning_collection}"
        
        headers = {
            "X-XSRF-TOKEN": csrf,
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        self.cookies = {
            "DSPACE-XSRF-COOKIE": csrf
        }

        # Debug: mostrar el payload ya serializado
        print("create_item payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print('owning_collection ', owning_collection)
        print('self.base_url ', self.base_url)
        print("csrf_token item_payload", csrf)
        print("self.cookies item_payload", self.cookies)
        print("Authorization", self.token)
        
        response = self.session.post(url, json=payload, headers=headers, cookies=self.cookies)
        
        print("create_item response:", response.status_code, response.text)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}

    def create_workspace_item(self, payload):
        """
        Paso 3. Crea un workspace item vacío en DSpace.
        Se espera que el payload incluya la clave "owningCollection" con el UUID de la colección,
        que se pasará como parámetro de consul1ta, y "sections" va vacío ya que solo creamos el item.
        """
        # Extraer y eliminar owningCollection del payload, ya que se pasará en la URL
        owning_collection = payload.pop("owningCollection", None)
        if not owning_collection:
            raise ValueError("El payload debe incluir 'owningCollection'.")

        # Construir la URL con el parámetro owningCollection
        url = f"{self.base_url}/submission/workspaceitems?owningCollection={owning_collection}"

        print("owning_collection: ", owning_collection)

        # Definir los headers
        headers = {
            "X-XSRF-TOKEN": self.cookies.get("DSPACE-XSRF-COOKIE"),
            "Content-Type": "application/json",
            "Authorization": self.token
        }

        print("headers: ", headers)
        print("self.cookies: ", self.cookies)

        # Realizar la solicitud POST enviando el payload en formato JSON
        response = self.session.post(url, json=payload.pop("sections", None), headers=headers, cookies=self.cookies)
        print("create_workspace_item response:", response.status_code, response.text)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            # Puedes manejar errores de forma más detallada si lo requieres
            return {"error": response.text, "status_code": response.status_code}

    def update_workspace_item_metadata(self, workspaceitem_id, payload):
        """
        Paso 4. Actualiza la metadata del workspaceitem en DSpace.
        Parámetros:
        - workspaceitem_id: ID del workspaceitem a actualizar.
        - payload: Lista de operaciones JSON Patch.
        """
        url = f"{self.base_url}/submission/workspaceitems/{workspaceitem_id}"
        headers = {
            "X-XSRF-TOKEN": self.cookies.get("DSPACE-XSRF-COOKIE"),
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        print("update_payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        response = self.session.patch(url, json=payload, headers=headers, cookies=self.cookies)
        print("update_workspace_item_metadata response:", response.status_code, response.text)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}

    

    ######################################################

   

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
        
    def logout(self):
        headers = {"Authorization": self.auth_token}
        response = requests.post(f"{self.base_url}/server/api/authn/logout", headers=headers)
        if response.status_code != 200:
            raise Exception("Error al cerrar sesión: " + response.text)
