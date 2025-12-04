from rest_framework import serializers
from .models import User, TrustBadge, UserActivity
from apps.user.validator import validate_image_file
from PIL import Image

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    profile_completion = serializers.IntegerField(read_only=True)
    location_lat = serializers.SerializerMethodField(read_only=True)
    location_lng = serializers.SerializerMethodField(read_only=True)
    badge = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'badge',
            'location',
            'location_lat',
            'location_lng',
            'location_text',
            'farm_size',
            'business_name',
            'profile_photo',
            'bio',
            'is_active',
            'is_staff',
            'is_superuser',
            'created_at',
            'updated_at',
            'profile_completion'
        ]
        read_only_fields = ['is_staff', 'is_superuser', 'is_active']
    
    def get_badge(self, obj):
        return obj.badge
    
    def get_location_lat(self, obj):
        return obj.location.y if obj.location else None
    
    def get_location_lng(self, obj):
        return obj.location.x if obj.location else None

class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        required=True,
        max_length=150,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150,
    )
    location_lat = serializers.FloatField(required=False)
    location_lng = serializers.FloatField(required=False)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'location_lat',
            'location_lng',
            'location_text',
            'farm_size',
            "business_name",
            'profile_photo',
            'bio'
        ]

    def validate(self, data):
        # At least one of coordinates or location_text may be required depending on your policy.
        lat = data.get("location_lat", None)
        lng = data.get("location_lng", None)
        location_text = data.get("location_text", None)

        # If coordinates provided, require both and validate ranges
        # ^ - XOR operator: True if exactly one of the two values is provided.
        # False if:
        # both are provided, or
        # neither is provided.
        if (lat is not None) ^ (lng is not None):
            raise serializers.ValidationError({
                "location": "Both location_lat and location_lng must be provided together."
            })

        if lat is not None and lng is not None:
            if not (-90 <= lat <= 90):
                raise serializers.ValidationError({"location_lat": ["Latitude must be between -90 and 90"]})
            if not (-180 <= lng <= 180):
                raise serializers.ValidationError({"location_lng": ["Longitude must be between -180 and 180"]})

        # Bio length is enforced by field, but double-check
        bio = data.get("bio")
        if bio is not None and len(bio) > 500:
            raise serializers.ValidationError({"bio": ["Bio must not exceed 500 characters"]})

        # Role-specific checks will be handled in the view where we have access to request.user.role
        return data

    def validate_profile_photo(self, value):
        # value is an InMemoryUploadedFile or similar
        if value:
            validate_image_file(value)
        return value

    def to_internal_value(self, data):
        # Use default implementation (keeps file objects intact)
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        # We'll handle saving in the view so this is not strictly necessary.
        return super().update(instance, validated_data)


class BadgeStatusSerializer(serializers.ModelSerializer):
    badge_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TrustBadge
        fields = [
            'badge_level',
            'badge_display',
            'is_phone_verified',
            'is_id_verified',
            'is_location_verified',
            'is_community_trusted',
            'transaction_count',
            'average_rating'
        ]

    def get_badge_display(self, obj):
        return obj.get_badge_display_name()        
    

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            'id',
            'user',
            'action_type',
            'description',
            'metadata',
            'ip_address',
            'created_at'
        ]
