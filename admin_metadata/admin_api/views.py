import json
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from dashboard.models import Register, Metadata, MetadataField

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_register(request):
    api_key = request.headers.get("X-API-KEY")
    if api_key != settings.API_KEY_CORFO:
        return Response({'error': 'No autorizado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # 1. Extraer datos base
        titulo = request.data.get('titulo')
        autor = request.data.get('autor')
        sistema_origen = request.data.get('sistema_origen', 'Sin información')
        identificador = request.data.get('identificador')
        proyecto_instrumento = request.data.get('proyecto_instrumento')
        coleccion = request.data.get('coleccion')
        archivo = request.FILES.get('archivo')
        metadata = request.data.get('metadata', [])

        # 2. Validar campos requeridos
        if not titulo or not autor or not coleccion:
            return Response({'error': 'Faltan campos requeridos: titulo o autor'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Crear registro base
        register = Register.objects.create(
            titulo=titulo,
            autor=autor,
            sistema_origen=sistema_origen,
            identificador=identificador,
            proyecto_instrumento=proyecto_instrumento,
            coleccion=coleccion,
            archivo=archivo
        )

        # 4. Parsear metadata si viene como string
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                return Response({'error': 'Formato inválido en metadata'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(metadata, list):
            return Response({'error': 'Metadata debe ser una lista de objetos'}, status=status.HTTP_400_BAD_REQUEST)

        # 5. Indexar campos enviados para verificar duplicación
        enviados = set()
        for meta in metadata:
            if not isinstance(meta, dict):
                return Response({'error': 'Cada metadato debe ser un objeto'}, status=status.HTTP_400_BAD_REQUEST)
            field_str = meta.get('metadata_field')
            if field_str:
                enviados.add(field_str.strip())

            # Validar campos base
            if not field_str or not meta.get('value'):
                return Response({'error': 'Faltan campos en metadata: metadata_field o value'}, status=status.HTTP_400_BAD_REQUEST)

            # Separar en partes
            parts = field_str.split('.')
            if len(parts) < 2:
                return Response({'error': f'Formato inválido en metadata_field: {field_str}'}, status=status.HTTP_400_BAD_REQUEST)

            schema = parts[0]
            element = parts[1]
            qualifier = parts[2] if len(parts) > 2 else None

            # Buscar MetadataField
            try:
                metadata_field = MetadataField.objects.get(schema=schema, element=element, qualifier=qualifier)
            except MetadataField.DoesNotExist:
                return Response({'error': f'MetadataField no encontrado: {field_str}'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear metadato
            Metadata.objects.create(
                text_value=meta.get('value'),
                text_lang=meta.get('lang', 'es_ES'),
                register=register,
                metadata_field=metadata_field
            )

        # 6. Generar automáticamente ciertos campos desde Register si no están en `metadata`
        auto_fields = {
            'dc.title': titulo,
            'dc.creator': autor,
            'dc.identifier': identificador,
            'cf.proyecto.instrumento': proyecto_instrumento,
            'dc.description': ' '  # Siempre agregarlo si no viene
        }

        for key, valor in auto_fields.items():
            if key not in enviados:
                parts = key.split('.')
                schema = parts[0]
                element = parts[1]
                qualifier = parts[2] if len(parts) > 2 else None

                try:
                    field = MetadataField.objects.get(schema=schema, element=element, qualifier=qualifier)
                except MetadataField.DoesNotExist:
                    continue  # Si no está definido en el modelo, omitir

                Metadata.objects.create(
                    text_value=valor if valor else ' ',
                    text_lang='es_ES',
                    register=register,
                    metadata_field=field
                )

        return Response({'message': 'Registro creado exitosamente'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    