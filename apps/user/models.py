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
    bio = models.TextField(null=True, blank=True, max_length=500)
    profile_photo = models.ImageField(upload_to='profile_photos', null=True, blank=True)

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


class TrustBadge(models.Model):
    BADGE_CHOICES = [
        ('new_user', 'New User'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('diamond', 'Diamond'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='badge'
    )
    
    # Verification fields
    is_phone_verified = models.BooleanField(
        default=True,        
    )
    is_id_verified = models.BooleanField(
        default=False
    )
    is_location_verified = models.BooleanField(default=False)
    is_community_trusted = models.BooleanField(default=False)

    # Transaction and Rating info
    transaction_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    # Badge level
    badge_level = models.CharField(max_length=10, choices=BADGE_CHOICES, default='new_user')

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_badge_display_name()}"

    def calculate_badge_level(self):
        """
        Determine the badge level based on the user's
        transaction history and rating.
        """
        rating = (self.average_rating or 0)
        count = self.transaction_count

        if count >= 100 and rating >= 4.8:
            self.badge_level = 'diamond'
        elif count >= 50 and rating >= 4.7:
            self.badge_level = 'gold'
        elif count >= 20 and rating >= 4.3:
            self.badge_level = 'silver'
        elif count >= 5 and rating >= 4.0:
            self.badge_level = 'bronze'
        else:
            self.badge_level = 'new_user'
        
        self.save(update_fields=['badge_level'])
    
    def get_badge_display_name(self):
        """Return human-friendly badge name"""
        display_map = {
            'new_user': 'New User',
            'bronze': 'Bronze Seller/Buyer',
            'silver': 'Silver Seller/Buyer',
            'gold': 'Gold Seller/Buyer',
            'diamond': 'Diamond Seller/Buyer',
        }
        return display_map.get(self.badge_level, 'New User')
        

class UserActivity(models.Model):
    class ActionTypes(models.TextChoices):
        LOGIN = "login", "Login"
        LOGIN_FAILED = "login_failed", "Login Failed"
        REGISTER = "register", "Register"
        PROFILE_UPDATE = "profile_update", "Profile Updated"
        LISTING_CREATE = "listing_create", "Listing Created"
        LISTING_UPDATE = "listing_update", "Listing Updated"
        LISTING_DELETE = "listing_delete", "Listing Deleted"
        PASSWORD_CHANGE = "password_change", "Password Changed"
        ACCOUNT_DELETE = "account_delete", "Account Deleted"

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ActionTypes.choices,
        default=ActionTypes.LOGIN,
        db_index=True
    )
    description = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # Fast queries: user activity history
            models.Index(fields=['user', 'created_at']),
            # Fast filtering by type (e.g., login attempts)
            models.Index(fields=['action_type']),
        ]
        ordering = ['-created_at']

    # --------------------------------------------------------------------
    # CLASSMETHOD: STANDARD WAY TO CREATE LOGS ANYWHERE IN THE APP
    # --------------------------------------------------------------------
    @classmethod
    def log_activity(cls, user, action_type, description, metadata=None, ip=None):
        return cls.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            metadata=metadata or {},
            ip_address=ip
        )
    
