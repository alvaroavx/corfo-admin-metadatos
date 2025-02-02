from django.db import models

class DspaceCollection(models.Model):
    id = models.CharField(max_length=255, primary_key=True)  # ID único de la colección
    uuid = models.CharField(max_length=255, unique=True)  # UUID
    name = models.CharField(max_length=255)  # Nombre de la colección
    handle = models.CharField(max_length=255, unique=True)  # Handle de la colección
    uri = models.URLField()  # URI de la colección
    last_updated = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return self.name