from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['is_staff', 'is_superuser', 'is_active']