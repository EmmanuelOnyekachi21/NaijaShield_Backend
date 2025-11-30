from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
import uuid
from django.shortcuts import get_object_or_404



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
        ('seller', 'Seller'),
    )
    public_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return f"{self.email}-{self.phone_number} ({self.role})"
    
    def get_full_name(self):
        """Get full name."""
        return self.first_name + ' ' + self.last_name


