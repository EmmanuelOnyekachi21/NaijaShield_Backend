from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.user.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        max_length=128,
        min_length=8,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        max_length=128,
        min_length=8,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'phone_number',
            'role',
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        roles = [choice[0] for choice in User.ROLE_CHOICES]
        if attrs['role'] not in roles:
            return serializer.ValidationError(
                {"role": "Invalid role."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2', None)
        return User.objects.create_user(**validated_data)