import json
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from dashboard.models import Register, Metadata, MetadataField

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_register(request):
    try:
        # 1. Extraer los datos del JSON de entrada
        titulo = request.data.get('titulo')
        autor = request.data.get('autor')
        sistema_origen = request.data.get('sistema_origen')
        coleccion = request.data.get('coleccion')
        metadata = request.data.get('metadata', [])  # Puede ser lista o string
        archivo = request.FILES.get('archivo')  # Capturar el archivo

        # 2. Validar campos principales
        if not titulo or not autor or not sistema_origen or not coleccion:
            return Response({'error': 'Faltan campos requeridos: titulo, autor o sistema_origen'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Crear el registro principal con el archivo (si existe)
        register = Register.objects.create(
            titulo=titulo,
            autor=autor,
            sistema_origen=sistema_origen,
            coleccion=coleccion,
            archivo=archivo  # Se almacena el archivo si fue enviado
        )

        # 4. Procesar los metadatos
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)  # Convertir a lista si es un string JSON
            except json.JSONDecodeError:
                return Response({'error': 'Formato inválido en metadata'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(metadata, list):
            return Response({'error': 'Metadata debe ser una lista de objetos'}, status=status.HTTP_400_BAD_REQUEST)

        for meta in metadata:
            if not isinstance(meta, dict):
                return Response({'error': 'Cada metadato debe ser un objeto'}, status=status.HTTP_400_BAD_REQUEST)

            metadata_field_str = meta.get('metadata_field')
            value = meta.get('value')
            lang = meta.get('lang', 'es_ES')

            if not metadata_field_str or not value:
                return Response({'error': 'Faltan campos en metadata: metadata_field o value'}, status=status.HTTP_400_BAD_REQUEST)

            # Procesar metadata_field
            parts = metadata_field_str.split('.')
            if len(parts) < 2:
                return Response({'error': f'Formato inválido en metadata_field: {metadata_field_str}'}, status=status.HTTP_400_BAD_REQUEST)

            schema = parts[0]
            element = parts[1]
            qualifier = parts[2] if len(parts) > 2 else None

            # Buscar MetadataField
            try:
                metadata_field = MetadataField.objects.get(schema=schema, element=element, qualifier=qualifier)
            except MetadataField.DoesNotExist:
                return Response({'error': f'MetadataField no encontrado: {metadata_field_str}'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear Metadata
            Metadata.objects.create(
                text_value=value,
                text_lang=lang,
                register=register,
                metadata_field=metadata_field,
            )

        return Response({'message': 'Registro creado exitosamente'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
