from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.agencies.models import Agency

User = get_user_model()

class AgencyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name', 'code']

class UserSerializer(serializers.ModelSerializer):
    agency = AgencyBriefSerializer(read_only=True)
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=Agency.objects.all(), source='agency', write_only=True, required=False, allow_null=True
    )
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone_number', 'agency', 'agency_id',
            'role', 'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_staff']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=Agency.objects.all(), source='agency', required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number',
            'agency_id', 'role'
        ]

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        # Role assignment permission checks
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            creator_role = request.user.role
            new_role = data.get('role', 'OPERATIONS_OFFICER')

            if new_role == 'SUPER_ADMIN' and creator_role != 'SUPER_ADMIN':
                raise serializers.ValidationError({'role': 'Only Super Admin can create Super Admins.'})

            if creator_role not in ['SUPER_ADMIN', 'AGENCY_ADMIN']:
                raise serializers.ValidationError({'role': 'You do not have permission to create users.'})

            # Agency Admin can only assign users to their own agency
            if creator_role == 'AGENCY_ADMIN' and request.user.agency:
                agency = data.get('agency')
                if agency and agency != request.user.agency:
                    raise serializers.ValidationError({'agency_id': 'You can only assign users to your own agency.'})

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)