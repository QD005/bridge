from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Agency

User = get_user_model()

class AgencyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class AgencySerializer(serializers.ModelSerializer):
    created_by = AgencyUserSerializer(read_only=True)
    
    class Meta:
        model = Agency
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']