import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_metadata.settings')
django.setup()

from dashboard.models import MetadataField

# Lista de campos de metadatos que deseas cargar
metadata_fields = [
    {'schema': 'dc', 'element': 'contributor', 'qualifier': 'advisor'},
    {'schema': 'dc', 'element': 'contributor', 'qualifier': 'author'},
    {'schema': 'dc', 'element': 'contributor', 'qualifier': 'editor'},
    {'schema': 'dc', 'element': 'contributor', 'qualifier': 'illustrator'},
    {'schema': 'dc', 'element': 'contributor', 'qualifier': 'other'},
    {'schema': 'dc', 'element': 'contributor', 'qualifier': None},
    {'schema': 'dc', 'element': 'coverage', 'qualifier': 'spatial'},
    {'schema': 'dc', 'element': 'coverage', 'qualifier': 'temporal'},
    {'schema': 'dc', 'element': 'creator', 'qualifier': None},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'accessioned'},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'available'},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'copyright'},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'created'},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'issued'},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'submitted'},
    {'schema': 'dc', 'element': 'date', 'qualifier': 'updated'},
    {'schema': 'dc', 'element': 'date', 'qualifier': None},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'abstract'},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'provenance'},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'sponsorship'},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'statementofresponsibility'},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'tableofcontents'},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'uri'},
    {'schema': 'dc', 'element': 'description', 'qualifier': 'version'},
    {'schema': 'dc', 'element': 'description', 'qualifier': None},
    {'schema': 'dc', 'element': 'format', 'qualifier': 'extent'},
    {'schema': 'dc', 'element': 'format', 'qualifier': 'medium'},
    {'schema': 'dc', 'element': 'format', 'qualifier': 'mimetype'},
    {'schema': 'dc', 'element': 'format', 'qualifier': None},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'citation'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'doi'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'govdoc'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'isbn'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'ismn'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'issn'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'other'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'scopus'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'sici'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'slug'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': 'uri'},
    {'schema': 'dc', 'element': 'identifier', 'qualifier': None},
    {'schema': 'dc', 'element': 'language', 'qualifier': 'iso'},
    {'schema': 'dc', 'element': 'language', 'qualifier': 'rfc3066'},
    {'schema': 'dc', 'element': 'language', 'qualifier': None},
    {'schema': 'dc', 'element': 'provenance', 'qualifier': None},
    {'schema': 'dc', 'element': 'publisher', 'qualifier': None},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'haspart'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'hasversion'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'isbasedon'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'isformatof'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'ispartof'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'ispartofseries'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'isreferencedby'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'isreplacedby'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'isversionof'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'replaces'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'requires'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': 'uri'},
    {'schema': 'dc', 'element': 'relation', 'qualifier': None},
    {'schema': 'dc', 'element': 'rights', 'qualifier': 'holder'},
    {'schema': 'dc', 'element': 'rights', 'qualifier': 'license'},
    {'schema': 'dc', 'element': 'rights', 'qualifier': 'uri'},
    {'schema': 'dc', 'element': 'rights', 'qualifier': None},
    {'schema': 'dc', 'element': 'source', 'qualifier': 'uri'},
    {'schema': 'dc', 'element': 'source', 'qualifier': None},
    {'schema': 'dc', 'element': 'subject', 'qualifier': 'classification'},
    {'schema': 'dc', 'element': 'subject', 'qualifier': 'ddc'},
    {'schema': 'dc', 'element': 'subject', 'qualifier': 'lcc'},
    {'schema': 'dc', 'element': 'subject', 'qualifier': 'lcsh'},
    {'schema': 'dc', 'element': 'subject', 'qualifier': 'mesh'},
    {'schema': 'dc', 'element': 'subject', 'qualifier': 'other'},
    {'schema': 'dc', 'element': 'subject', 'qualifier': None},
    {'schema': 'dc', 'element': 'title', 'qualifier': 'alternative'},
    {'schema': 'dc', 'element': 'title', 'qualifier': None},
    {'schema': 'dc', 'element': 'type', 'qualifier': None},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'actividadeconomica'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'etnia'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'genero'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'nacionalidad'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'nombre'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'razonsocial'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'rut'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'sectororigen'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'tamanoempresa'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'tipoparticipante'},
    {'schema': 'cf', 'element': 'beneficiario', 'qualifier': 'tipopersona'},
    {'schema': 'cf', 'element': 'comite', 'qualifier': 'fecha'},
    {'schema': 'cf', 'element': 'comite', 'qualifier': 'nombre'},
    {'schema': 'cf', 'element': 'comite', 'qualifier': 'sesion'},
    {'schema': 'cf', 'element': 'comuna', 'qualifier': 'ejecucion'},
    {'schema': 'cf', 'element': 'comuna', 'qualifier': 'impacto'},
    {'schema': 'cf', 'element': 'comuna', 'qualifier': 'postulacion'},
    {'schema': 'cf', 'element': 'consultor', 'qualifier': 'especialidad'},
    {'schema': 'cf', 'element': 'consultor', 'qualifier': 'nombre'},
    {'schema': 'cf', 'element': 'consultor', 'qualifier': 'rut'},
    {'schema': 'cf', 'element': 'contraparte', 'qualifier': 'nombre'},
    {'schema': 'cf', 'element': 'corfo', 'qualifier': 'beneficiarioreal'},
    {'schema': 'cf', 'element': 'corfo', 'qualifier': 'rut'},
    {'schema': 'cf', 'element': 'costo', 'qualifier': 'beneficiarioaprobado'},
    {'schema': 'cf', 'element': 'costo', 'qualifier': 'beneficiarioreal'},
    {'schema': 'cf', 'element': 'costo', 'qualifier': 'corfoaprobado'},
    {'schema': 'cf', 'element': 'costo', 'qualifier': 'corforeal'},
    {'schema': 'cf', 'element': 'costo', 'qualifier': 'tipomoneda'},
    {'schema': 'cf', 'element': 'costo', 'qualifier': 'total'},
    {'schema': 'cf', 'element': 'ejecutivo', 'qualifier': 'nombre'},
    {'schema': 'cf', 'element': 'ejecutivo', 'qualifier': 'rut'},
    {'schema': 'cf', 'element': 'fecha', 'qualifier': 'ano'},
    {'schema': 'cf', 'element': 'fecha', 'qualifier': 'inicio'},
    {'schema': 'cf', 'element': 'fecha', 'qualifier': 'liberacion'},
    {'schema': 'cf', 'element': 'fecha', 'qualifier': 'postulacion'},
    {'schema': 'cf', 'element': 'fecha', 'qualifier': 'termino'},
    {'schema': 'cf', 'element': 'instrumentoasociado', 'qualifier': 'nombre'},
    {'schema': 'cf', 'element': 'instrumentoasociado', 'qualifier': 'url'},
    {'schema': 'cf', 'element': 'objetivo', 'qualifier': 'especifico'},
    {'schema': 'cf', 'element': 'objetivo', 'qualifier': 'general'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'cluster'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'estado'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'estadonombre'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'inst'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'instrumento'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'tipopostulacion'},
    {'schema': 'cf', 'element': 'proyecto', 'qualifier': 'unidadorigen'},
    {'schema': 'cf', 'element': 'region', 'qualifier': 'beneficiario'},
    {'schema': 'cf', 'element': 'region', 'qualifier': 'ejecucion'},
    {'schema': 'cf', 'element': 'region', 'qualifier': 'impacto'},
    {'schema': 'cf', 'element': 'region', 'qualifier': 'postulacion'},
    {'schema': 'cf', 'element': 'sistemaorigen', 'qualifier': None}
]

# Cargar los datos en la base de datos
for field in metadata_fields:
    metadata_field, created = MetadataField.objects.get_or_create(
        schema=field['schema'],
        element=field['element'],
        qualifier=field['qualifier']
    )
    if created:
        print(f"Creado: {metadata_field}")
    else:
        print(f"Ya existe: {metadata_field}")

# Ejecutar el comando
# python load_metadatafields.py
