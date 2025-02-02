from rest_framework import serializers
from dashboard.models import Register

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ['id', 'titulo', 'autor', 'sistema_origen', 'fecha_carga']  # Agrega los campos relevantes
