from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view
from dashboard.models import Register, Metadata
from dspace_api.models import DspaceCollection
from dspace_api.services import *

@api_view(['GET'])
def dashboard(request):
    """
    Vista para listar todos los registros cargados en una tabla.
    """
    fetch_and_update_collections()
    registros = Register.objects.all()
    return render(request, 'metadata/dashboard.html', {'registros': registros})

def registro_detalle(request, id):
    """
    Vista de lectura del registro
    """
    registro = get_object_or_404(Register, id=id)
    # Obtener la colección asociada si existe
    coleccion = None
    if registro.coleccion:  # Solo intenta buscar si el handle no está vacío
        coleccion = DspaceCollection.objects.filter(handle=registro.coleccion).first()
    # Obtener los metadatos asociados al registro
    metadatos = registro.metadata.all()  # Obtiene todos los metadatos asociados a este registro
    return render(request, 'metadata/registro_detalle.html', {
        'registro': registro,
        'metadatos': metadatos,
        'coleccion': coleccion,
    })

def registro_modificar(request, id):
    """
    Vista para modificar los datos del registro
    """
    registro = get_object_or_404(Register, id=id)
    # Obtener las colecciones disponibles
    collections = DspaceCollection.objects.all()
    # Obtener los metadatos asociados al registro
    metadatos = registro.metadata.all()  # Obtiene todos los metadatos asociados a este registro
    return render(request, 'metadata/registro_modificar.html', {'registro': registro, 'metadatos': metadatos, 'collections': collections})

def registro_aprobar(request, id=None):
    """
    Actualiza el estado del registro o registros a 'aprobado',
    solo si tienen una colección asignada.
    Redirige a la vista del detalle si es un único registro.
    Redirige al dashboard si son múltiples registros.
    """
    if request.method == 'POST':  # Para aprobar múltiples registros
        ids = request.POST.getlist('registro_ids')  # Obtiene la lista de IDs
        if not ids:  # Si no hay IDs enviados, muestra un error
            messages.error(request, "No se encontraron registros válidos para aprobar.")
            return redirect('dashboard')

        # Filtra los registros por los IDs proporcionados
        registros = Register.objects.filter(id__in=ids)

        if not registros.exists():
            messages.error(request, "No se encontraron registros válidos.")
            return redirect('dashboard')

        # Verifica si hay registros sin colección asignada
        sin_coleccion = registros.filter(coleccion__isnull=True) | registros.filter(coleccion="")

        if sin_coleccion.exists():
            messages.error(request, "Algunos registros no tienen colección asignada y no pueden ser aprobados.")
            return redirect('dashboard')

        # Actualiza el estado a 'aprobado' para todos los registros con colección asignada
        registros.update(estado='aprobado')
        messages.success(request, f"Se han aprobado {len(ids)} registros.")
        return redirect('dashboard')  # Redirige al dashboard

    elif request.method == 'GET' and id:  # Para aprobar un único registro desde un botón
        # Obtiene el registro por ID
        registro = get_object_or_404(Register, id=id)

        # Verifica si el registro tiene colección asignada
        if not registro.coleccion:
            messages.error(request, "Este registro no tiene colección asignada y no puede ser aprobado.")
            return redirect('registro_detalle', id=registro.id)

        # Actualiza el estado a 'aprobado'
        registro.estado = 'aprobado'
        registro.save()

        messages.success(request, f"El registro '{registro.titulo}' ha sido aprobado.")
        return redirect('registro_detalle', id=registro.id)  # Redirige al detalle del registro

    # Respuesta para solicitudes no permitidas
    return JsonResponse({"error": "Método no permitido"}, status=405)

def registro_rechazar(request, id=None):
    """
    Actualiza el estado del registro o registros a 'rechazado'.
    Redirige a la vista del detalle si es un único registro.
    Redirige al dashboard si son múltiples registros.
    """
    if request.method == 'POST':  # Para rechazar múltiples registros
        ids = request.POST.getlist('registro_ids')  # Obtiene la lista de IDs
        if not ids:  # Si no hay IDs enviados, muestra un error
            messages.error(request, "No se encontraron registros válidos para rechazar.")
            return redirect('dashboard')

        # Filtra los registros por los IDs proporcionados
        registros = Register.objects.filter(id__in=ids)
        if not registros.exists():
            messages.error(request, "No se encontraron registros válidos.")
            return redirect('dashboard')

        # Actualiza el estado a 'rechazado' para todos los registros
        registros.update(estado='rechazado')
        messages.success(request, f"Se han rechazado {len(ids)} registros.")
        return redirect('dashboard')  # Redirige al dashboard

    elif request.method == 'GET' and id:  # Para rechazar un único registro desde un botón
        # Obtiene el registro por ID
        registro = get_object_or_404(Register, id=id)

        # Actualiza el estado a 'rechazado'
        registro.estado = 'rechazado'
        registro.save()

        messages.success(request, f"El registro '{registro.titulo}' ha sido rechazado.")
        return redirect('registro_detalle', id=registro.id)  # Redirige al detalle del registro

    # Respuesta para solicitudes no permitidas
    return JsonResponse({"error": "Método no permitido"}, status=405)

def registro_guardar(request, id):
    """
    Metodo POST: Vista para guardar los cambios realizados en un registro.
    """
    # Obtener el registro o mostrar error 404 si no existe
    registro = get_object_or_404(Register, id=id)

    if request.method == "POST":
        # Actualizar los campos del registro, evitando sobreescribir `fecha_carga`
        registro.titulo = request.POST.get("titulo", registro.titulo)
        registro.autor = request.POST.get("autor", registro.autor)
        registro.sistema_origen = request.POST.get("sistema_origen", registro.sistema_origen)
        registro.coleccion = request.POST.get("coleccion", registro.coleccion)
        registro.estado = request.POST.get("estado", registro.estado)

        # Guardar el registro actualizado
        registro.save()

        # Actualizar los metadatos asociados al registro
        for key, value in request.POST.items():
            if key.startswith("metadata_"):
                # Extraer el ID del metadato desde el nombre del campo
                metadata_id = key.split("_")[1]
                try:
                    # Buscar el metadato correspondiente
                    metadata = Metadata.objects.get(id=metadata_id, register=registro)
                    # Solo actualizamos si el valor ha cambiado
                    if metadata.text_value != value:
                        metadata.text_value = value
                        metadata.save()
                except Metadata.DoesNotExist:
                    # Si no se encuentra el metadato, loguear o manejar el error de alguna manera
                    pass

        # Mensaje de éxito
        messages.success(request, "Los cambios se han guardado exitosamente.")

        # Redirigir a la página de detalle del registro
        return redirect("registro_detalle", id=registro.id)

    # Si no es un método POST, redirigir a la página de detalle del registro
    return redirect("registro_detalle", id=registro.id)

def registro_enviar(request, id=None):
    # Aquí obtienes el registro o varios
    registros = Register.objects.filter(id=id) if id else Register.objects.all()
    return render(request, "metadata/registro_enviar.html", {"registros": registros})

def estado_tarea(request, id):
    # Obtener el estado del envio de un registro
    registro = get_object_or_404(Register, id=id)
    
    pasos = {
        'autenticado': registro.estado_envio == 'autenticado',
        'workspace': registro.estado_envio == 'workspace_creado',
        'metadata': registro.estado_envio == 'metadata_ingresada',
        'archivo': registro.estado_envio == 'archivo_subido',
        'publicado': registro.estado_envio == 'publicado'
    }
    
    return JsonResponse({'pasos': pasos})

def ejecutar_envio(request, id):
    registro = Register.objects.get(pk=id)
    errores = []  # Lista para almacenar errores

    # Paso 1: Autenticación
    token = autenticar_dspace()
    if not token:
        errores.append("Error en autenticación con DSpace")
    
    # Paso 2: Crear workspace item
    workspace_id = None
    if token:
        workspace_id = crear_workspace_item(token, registro)
        if not workspace_id:
            errores.append("Error al crear workspace item")

    # Paso 3: Agregar metadatos
    metadata_actualizada = None
    if workspace_id:
        metadata_actualizada = actualizar_metadata(token, workspace_id, registro)
        if not metadata_actualizada:
            errores.append("Error al actualizar metadatos")

    # Paso 4: Subir archivo
    archivo_subido = None
    if metadata_actualizada:
        archivo_subido = subir_archivo(token, workspace_id, registro)
        if archivo_subido is None:
            errores.append("Error al subir archivo")

    # Paso 5: Publicar item
    if archivo_subido:
        publicado = publicar_item(token, workspace_id, registro)
        if not publicado:
            errores.append("Error al publicar el registro")

    # Si hubo errores, devolverlos
    if errores:
        registro.estado_envio = 'error'
        registro.save()
        return JsonResponse({"success": False, "errores": errores})

    return JsonResponse({"success": True})
