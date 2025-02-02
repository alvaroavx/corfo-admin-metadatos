"""
URL configuration for admin_metadata project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import *

urlpatterns = [
    # Ruta del Administrador
    path('admin/', admin.site.urls),
    # Ruta para la API
    path('api/', include('admin_api.urls')),
    # Vistas del dashboard
    path('dashboard/', dashboard, name='registros'),
    # Vistas de los registros
    path('dashboard/<int:id>/view', registro_detalle, name='registro_detalle'),
    path('dashboard/<int:id>/edit', registro_modificar, name='registro_modificar'),
    path('dashboard/<int:id>/save', registro_guardar, name='registro_guardar'),
    # Aprobacion para un único y multiples registro
    path('dashboard/<int:id>/approve/', registro_aprobar, name='registro_aprobar'),
    path('dashboard/approve/', registro_aprobar, name='registro_aprobar_multiple'),
    # Rechazo para un único y varios registros
    path('dashboard/<int:id>/reject/', registro_rechazar, name='registro_rechazar'),
    path('dashboard/reject/', registro_rechazar, name='registro_rechazar'),
    # Envio a DSpace
    path('dashboard/<int:id>/send', registro_enviar, name='registro_enviar'),
    path('dashboard/send/', registro_enviar, name='registro_enviar_multiple'),
    path('estado-tarea/<int:id>/', estado_tarea, name='estado_tarea'),
    path('ejecutar-envio/<int:id>/', ejecutar_envio, name='ejecutar_envio'),
]
# Manejo de archivos
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)