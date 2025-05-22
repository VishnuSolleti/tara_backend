from rest_framework import serializers
from .models import ServiceTask

class ServiceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTask
        fields = '__all__'
