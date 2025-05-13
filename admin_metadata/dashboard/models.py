from django.db import models

class Register(models.Model):
    """
    Modelo para los registros que almacenan la información principal de cada entrada.
    """
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
    ]
    ESTADOS_ENVIO = [
        ('no_enviado', 'No Enviado'),
        ('autenticado', 'Autenticado'),
        ('workspace_creado', 'Workspace creado'),
        ('item_creado', 'Item creado'),
        ('metadata_ingresada', 'Metadata ingresada'),
        ('archivo_subido', 'Archivo subido'),
        ('publicado', 'Publicado'),
        ('error', 'Error'),
    ]
    # Informacion del Admin
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=255, verbose_name="Título") # dc.title
    autor = models.CharField(max_length=255, verbose_name="Autor") # dc.creator
    sistema_origen = models.CharField(null=True, blank=True, max_length=255, verbose_name="Sistema de origen")
    fecha_carga = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de carga") # dc.date
    coleccion = models.CharField(max_length=255, verbose_name="Colección de destino")
    identificador = models.CharField(max_length=255, null=True, blank=True, verbose_name="Identificador") # dc.identifier
    proyecto_instrumento = models.CharField(max_length=255, null=True, blank=True, verbose_name="Proyecto Instrumento") # cf.proyectoinstrumento
    # Informacion de DSpace
    workspaceitem_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="WorkSpaceItem ID")
    item_uuid = models.CharField(max_length=100, null=True, blank=True, verbose_name="Item UUID")
    handle = models.CharField(max_length=255, null=True, blank=True, verbose_name="Handle")
    inArchive = models.BooleanField(null=True, blank=True, verbose_name="Archivado?")
    discoverable = models.BooleanField(null=True, blank=True, verbose_name="Descubrible?")
    withdrawn = models.BooleanField(null=True, blank=True, verbose_name="Retirado?")
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='pendiente',
        verbose_name="Estado",
    )
    estado_envio = models.CharField(
        max_length=20,
        choices=ESTADOS_ENVIO,
        default='no_enviado',
        verbose_name="Estado de envío"
    )
    archivo = models.FileField(
        upload_to='archivos/', 
        blank=True, 
        null=True, 
        verbose_name="Archivo adjunto"
    )

    def __str__(self):
        return self.titulo


class MetadataField(models.Model):
    """
    Modelo que define los campos de metadatos basados en un esquema.
    """
    id = models.AutoField(primary_key=True)
    schema = models.CharField(max_length=50, choices=[('dc', 'Dublin Core'), ('cf', 'Corfo')], verbose_name="Esquema")
    element = models.CharField(max_length=100, verbose_name="Elemento")
    qualifier = models.CharField(max_length=100, null=True, blank=True, verbose_name="Calificador")

    def __str__(self):
        return f"{self.schema}.{self.element}" + (f".{self.qualifier}" if self.qualifier else "")


class Metadata(models.Model):
    """
    Modelo que une los registros con los campos de metadata y sus valores.
    """
    id = models.AutoField(primary_key=True)
    text_value = models.TextField(verbose_name="Valor del metadato")
    text_lang = models.CharField(max_length=10, default='es_ES', verbose_name="Idioma")
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='metadata', verbose_name="Registro")
    metadata_field = models.ForeignKey(MetadataField, on_delete=models.CASCADE, related_name='metadata', verbose_name="Campo de Metadata")

    def __str__(self):
        return f"{self.metadata_field} -> {self.text_value[:50]}..."  # Muestra un resumen del valor

