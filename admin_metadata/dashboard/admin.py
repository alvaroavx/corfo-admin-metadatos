from django.contrib import admin
from django.utils.html import format_html
from dashboard.models import Register, MetadataField, Metadata
from dspace_api.models import DspaceCollection

@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'sistema_origen', 'coleccion', 'estado', 'fecha_carga', 'archivo_link')
    list_filter = ('estado', 'sistema_origen', 'coleccion', 'fecha_carga')
    search_fields = ('titulo', 'autor', 'sistema_origen', 'coleccion')

    def archivo_link(self, obj):
        if obj.archivo:
            return format_html('<a href="{}" target="_blank">Ver archivo</a>', obj.archivo.url)
        return "No adjunto"
    archivo_link.allow_tags = True
    archivo_link.short_description = "Archivo"

@admin.register(MetadataField)
class MetadataFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'element', 'qualifier')
    list_filter = ('schema',)
    search_fields = ('element', 'qualifier')

@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'register', 'metadata_field', 'text_value', 'text_lang')
    list_filter = ('text_lang',)
    search_fields = ('text_value',)

@admin.register(DspaceCollection)
class DspaceCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'handle', 'uuid', 'uri', 'last_updated')  # Columnas visibles en la lista
    search_fields = ('name', 'handle', 'uuid')  # Campos habilitados para búsqueda
    list_filter = ('last_updated',)  # Filtro lateral
    ordering = ('name',)  # Ordenar las colecciones por nombre
    # Opcional: Campos de solo lectura si no quieres que los editen desde el admin
    readonly_fields = ('id', 'uuid', 'handle', 'uri', 'last_updated')