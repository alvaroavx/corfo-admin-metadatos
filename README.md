# Admin Metadatos CORFO

## Descripción
Admin Metadatos CORFO es una plataforma desarrollada en Python/Django para gestionar registros con metadatos basados en el estándar Dublin Core. Permite la recepción, modificación, aprobación y envío de registros a DSpace 7.x.

## Tecnologías
- **Lenguaje:** Python 3.11.4
- **Framework:** Django 5.1.4
- **Base de datos:** PostgreSQL
- **Cola de tareas:** Celery con Redis
- **Integración:** API REST de DSpace 7.x

## Instalación

### Prerrequisitos
- Python 3.11.4
- SQLite 3
- Redis (para Celery)
- Virtualenv

### Pasos
1. Clonar el repositorio:
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd admin-metadatos-corfo
   ```
2. Crear y activar el entorno virtual:
   ```sh
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Configurar las variables de entorno en `settings.py`:
   ```python
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
   
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_ACCEPT_CONTENT = ['json']
   CELERY_TASK_SERIALIZER = 'json'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   
   DSPACE_USERNAME = "avargas@opengeek.cl"
   DSPACE_PASSWORD = "184dgy.A"
   DSPACE_API_URL = "https://repositoriodigital.corfo.cl/server/api"
   ```
5. Aplicar migraciones:
   ```sh
   python manage.py migrate
   ```
6. Cargar los metadatos:
   ```sh
   python load_metadatafields.py
   ```
7. Crear un usuario administrador:
   ```sh
   python manage.py createsuperuser
   ```
8. Ejecutar el servidor:
   ```sh
   python manage.py runserver
   ```


## Endpoints de la API

### Insertar Registro
**Método:** `POST`  
**URL:** `/api/insertarRegistro/`

#### Descripción
Este endpoint permite insertar un registro en el sistema, incluyendo metadatos asociados y un archivo.

#### Parámetros del Request

- `titulo` (required): Título del registro.
- `autor` (required): Autor del registro.
- `sistema_origen` (required): El sistema desde donde proviene el registro (por ejemplo, "SGP").
- `archivo` (required): El archivo a subir (debe ser un archivo válido como PDF, imagen, etc.).
- `metadata` (required): Un conjunto de metadatos en formato JSON.
- `coleccion` (required): Identificador de la colección a la que se asociará el registro.

#### Ejemplo con cURL
```sh
curl --location 'http://127.0.0.1:8000/api/insertarRegistro/' --form 'titulo="Otro ejemplo de archivo 3"' --form 'autor="Crescente Molina"' --form 'sistema_origen="SGP"' --form 'archivo=@"/C:/Users/alvax/OneDrive/Escritorio/Bases-FFOIP-2024.pdf"' --form 'metadata="[ 
    {
      "metadata_field": "cf.beneficiario.razonsocial",
      "value": "Comercilizadora BF Limitada",
      "lang": "es_ES"
    },
    {
      "metadata_field": "cf.costo.tipomoneda",
      "value": "14998896",
      "lang": "es_ES"
    },
    {
      "metadata_field": "cf.fecha.ano",
      "value": "2012",
      "lang": "es_ES"
    },
    {
      "metadata_field": "cf.proyecto.cluster",
      "value": "Industrias creativas (audio-visuales-literatura)",
      "lang": "es_ES"
    },
    {
      "metadata_field": "cf.proyecto.instrumento",
      "value": "Distribución Audiovisual",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.contributor.author",
      "value": "Marialy Rivas - Director",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.contributor.author",
      "value": "Marialy Rivas, Camila Gutiérrez, Pedro Peirano y Sebastián Sepúlveda",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.contributor.author",
      "value": "Juan Ignacio Correa, Mariane Hartard - Productor ejecutivo",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.contributor.author",
      "value": "Sergio Armstrong - Dirección de fotografía",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.contributor.author",
      "value": "Polin Garbisu - Dirección de arte",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.contributor.author",
      "value": "Francisca Valenzuela, Javiera Mena - Música original",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.date",
      "value": "2012",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.date.accessioned",
      "value": "2013-01-25T14:15:43Z"
    },
    {
      "metadata_field": "dc.date.available",
      "value": "2013-01-25T14:15:43Z"
    },
    {
      "metadata_field": "dc.date.issued",
      "value": "2013-01-25"
    },
    {
      "metadata_field": "dc.description.abstract",
      "value": "Daniela es una chica de 17 años criada en el seno de una estricta familia Evangélica. Rebelde por naturaleza intentará seguir el “buen camino” luego de ser desenmascarada como una fornicadora por sus impactados padres. En el camino hacia la salvación descubrirá un devastador obstáculo para conseguir la anhelada armonía espiritual, las pulsiones de una sexualidad irreconciliable con los cánones de su religión.",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.format",
      "value": "35 mm",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.identifier.uri",
      "value": "http://repositoriodigital.corfo.cl/xmlui/handle/11373/8108"
    },
    {
      "metadata_field": "dc.language.iso",
      "value": "es",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.subject",
      "value": "Drama",
      "lang": "es_ES"
    },
    {
      "metadata_field": "dc.title",
      "value": "Joven y alocada",
      "lang": "es_ES"
    }
  ]"' --form 'coleccion="11373/1497"'
```

#### Ejemplo con Postman
1. Seleccionar método `POST`.
2. URL: `http://127.0.0.1:8000/api/insertarRegistro/`.
3. En la pestaña **Body**, seleccionar **form-data**.
4. Ingresar los siguientes campos:
   - `titulo`: "Otro ejemplo de archivo 3"
   - `autor`: "Crescente Molina"
   - `sistema_origen`: "SGP"
   - `archivo`: Seleccionar el archivo desde tu sistema.
   - `metadata`: Ingresar el JSON del conjunto de metadatos (como se mostró en el ejemplo de cURL).
   - `coleccion`: "11373/1497"

#### Posibles respuestas

**Éxito (201 Created)**:
```json
{
    "message": "Registro creado exitosamente"
}
```

**Error (400 Bad Request)**:
```json
{
    "error": "Faltan campos requeridos: titulo, autor o sistema_origen"
}
```

**Error con el archivo**:
```json
{
    "error": "El archivo no fue enviado correctamente"
}
```

## Usuarios Iniciales
| Usuario  | Contraseña  | Rol        |
|----------|------------|------------|
| root     | 184dgy.A   | superadmin |

## Contribución
Para contribuir, por favor sigue el flujo de trabajo basado en `git flow`. Se recomienda crear una rama por funcionalidad y realizar `pull requests` antes de fusionar con la rama principal.

## Licencia
Este proyecto es de uso interno de CORFO y no cuenta con una licencia pública.

