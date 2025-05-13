from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view
from dashboard.models import Register, Metadata
from dspace_api.models import DspaceCollection
from dspace_api.services import *
# pdf y csv
from xhtml2pdf import pisa
from io import BytesIO
import csv

@api_view(['GET'])
@login_required
def dashboard(request):
    """
    Vista para listar todos los registros cargados en una tabla.
    """
    # Actualiza el listado de colecciones interno
    fetch_and_update_collections()

    # Capturar filtros
    estado = request.GET.get('estado')
    autor = request.GET.get('autor')
    identificador = request.GET.get('identificador')
    proyecto_instrumento = request.GET.get('proyecto_instrumento')
    coleccion = request.GET.get('coleccion')

    registros = Register.objects.all()

    if estado:
        registros = registros.filter(estado=estado)
    if autor:
        registros = registros.filter(autor=autor)
    if identificador:
        registros = registros.filter(identificador=identificador)
    if proyecto_instrumento:
        registros = registros.filter(proyecto_instrumento=proyecto_instrumento)
    if coleccion:
        registros = registros.filter(coleccion=coleccion)
    
    return render(request, 'metadata/dashboard.html', {
        'registros': registros,
        'estado_seleccionado': estado,
        'autores': Register.objects.values_list('autor', flat=True).distinct().order_by('autor'),
        'identificadores': Register.objects.values_list('identificador', flat=True).distinct().order_by('identificador'),
        'proyectos': Register.objects.values_list('proyecto_instrumento', flat=True).distinct().order_by('proyecto_instrumento'),
        'colecciones': Register.objects.values_list('coleccion', flat=True).distinct().order_by('coleccion'),
        'filtros': {
            'autor': autor,
            'identificador': identificador,
            'proyecto_instrumento': proyecto_instrumento,
            'coleccion': coleccion
        }
    })

@login_required
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
        'DSPACE_URL': settings.DSPACE_URL
    })

@login_required
def registro_descargar_pdf(request, id):
    registro = get_object_or_404(Register, id=id)
    metadatos = registro.metadata.all()

    html = render_to_string('metadata/registro_pdf.html', {
        "registro": registro,
        "metadatos": metadatos
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="registro_{registro.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generando el PDF", status=500)

    return response

@login_required
def registro_descargar_csv(request, id):
    registro = get_object_or_404(Register, id=id)
    metadatos = registro.metadata.all()

    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="registro_{registro.id}.csv"'

    writer = csv.writer(response)
    
    # Escribir encabezado de datos generales
    writer.writerow(['Campo', 'Valor'])
    writer.writerow(['ID', registro.id])
    writer.writerow(['Título', registro.titulo])
    writer.writerow(['Autor', registro.autor])
    writer.writerow(['Sistema de Origen', registro.sistema_origen or ''])
    writer.writerow(['Identificador', registro.identificador or ''])
    writer.writerow(['Proyecto Instrumento', registro.proyecto_instrumento or ''])
    writer.writerow(['Fecha de Carga', registro.fecha_carga.strftime("%d/%m/%Y %H:%M")])
    writer.writerow(['Colección', registro.coleccion or ''])
    writer.writerow(['Estado', registro.estado])
    
    if registro.handle:
        writer.writerow(['URL en DSpace', f'http://repositoriodigital.corfo.cl/handle/{registro.handle}'])

    # Línea vacía para separar
    writer.writerow([])
    writer.writerow(['Metadatos Asociados'])

    # Encabezado de metadatos
    writer.writerow(['Campo', 'Valor'])

    for meta in metadatos:
        writer.writerow([str(meta.metadata_field), meta.text_value])

    return response


@login_required
def registro_modificar(request, id):
    """
    Vista para modificar los datos del registro
    """
    registro = get_object_or_404(Register, id=id)
    # Obtener las colecciones disponibles
    collections = DspaceCollection.objects.all()
    # Obtener los metadatos asociados al registro
    metadatos = registro.metadata.all()  # Obtiene todos los metadatos asociados a este registro
    return render(request, 'metadata/registro_modificar.html', {
        'registro': registro, 
        'metadatos': metadatos, 
        'collections': collections,
        'DSPACE_URL': settings.DSPACE_URL
    })

@login_required
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

@login_required
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

@login_required
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
        registro.identificador = request.POST.get("identificador", registro.identificador)
        registro.proyecto_instrumento = request.POST.get("proyecto_instrumento", registro.proyecto_instrumento)
        registro.coleccion = request.POST.get("coleccion", registro.coleccion)
        registro.estado = request.POST.get("estado", registro.estado)

        # Si se marcó eliminar archivo, eliminarlo del modelo
        if request.POST.get("eliminar_archivo") and registro.archivo:
            registro.archivo.delete(save=False)
            registro.archivo = None

        # Si se subió un nuevo archivo, reemplazarlo
        archivo_nuevo = request.FILES.get("archivo")
        if archivo_nuevo:
            registro.archivo = archivo_nuevo

        # Si el registro estaba rechazado y es modificado, cambia a pendiente
        if registro.estado == "rechazado":
            registro.estado = "pendiente"

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

@login_required
def registro_eliminar(request, id):
    registro = get_object_or_404(Register, id=id)

    if registro.estado == "rechazado":
        registro.delete()
        messages.success(request, "Registro eliminado correctamente.")
    else:
        messages.error(request, "Solo se pueden eliminar registros rechazados.")

    return redirect("registros")

@login_required
def registro_enviar(request, id=None):
    """Vista que devuelve el estado del envio del registro"""
    if not id:
        return JsonResponse({"error": "El parámetro 'id' es requerido"}, status=400)
     # Ejecutar el flujo de envío
    data = send_item_flow(id)
    if data.get("success") is False:
        return JsonResponse(data, status=400)
    # Redirigir al detalle del registro
    return redirect('registro_detalle', id=id)
    #return JsonResponse(data)

@login_required
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
