from django.urls import path
from .views import create_register

urlpatterns = [
    path('insertarRegistro/', create_register, name='create_register'),  # Endpoint para insertar registros
]
