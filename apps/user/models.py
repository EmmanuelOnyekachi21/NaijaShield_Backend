from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
import uuid
from django.shortcuts import get_object_or_404
from django.contrib.gis.db import models as gis_models



class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError("users must have an email address.")
        if not phone_number:
            raise ValueError("users must have a phone number.")
        if not password:
            raise ValueError("users must have a password.")
        email = self.normalize_email(email)
        phone_number = '+234' + phone_number[1:] if phone_number.startswith('0') else phone_number
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone_number, password, **extra_fields)
    
    def get_object_by_public_id(self, public_id):
        return get_object_or_404(self, public_id=public_id)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('co-ops', 'Cooperative'),
    )
    public_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone_number = models.CharField(max_length=15, unique=True, null=False, blank=False)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # New fields
    location = gis_models.PointField(srid=4326, null=True, blank=True)
    location_text = models.CharField(max_length=255, null=True, blank=True)

    farm_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    business_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_photo = models.URLField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return f"{self.email}-{self.phone_number} ({self.role})"
    
    def get_full_name(self):
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name
        return self.email
    
    @property
    def profile_completion(self):
        total = 0

        # ------------- BASE FIELDS (60%) ----------------
        # phone + email → always filled = 10%
        total += 10

        # first_name - 10%
        if self.first_name:
            total += 10

        # last_name - 10%
        if self.last_name:
            total += 10

        # location - 20%
        if self.location:
            total += 20

        # location_text - 10%
        if self.location_text:
            total += 10

        # --------------- ROLE SPECIFIC (max 30–40%) -------------------- #
        role = self.role.lower()

        if role == 'farmer':
            if self.farm_size:
                total += 20
            if self.bio:
                total += 10

        elif role == "buyer":
            if self.bio:
                total += 30

        elif role == "co-ops":
            if self.business_name:
                total += 20
            if self.bio:
                total += 20

        # ---------- BONUS PHOTO (10%) ----------
        if self.profile_photo:
            total += 10

        return total  # integer



