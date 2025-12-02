from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'role', 'is_active', 'is_staff', 'is_superuser', 'profile_completion')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'phone_number')
    ordering = ('created_at',)

    fieldsets = (
        (None, {'fields': (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'bio',
            'profile_photo',
            'location',
            'location_text',
            'farm_size',
            'business_name',
        )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'phone_number',
                    'password1',
                    'password2',
                    'bio',
                    'profile_photo',
                    'location',
                    'location_text',
                    'farm_size',
                    'business_name',
                    'role'
                ),
            },
        ),
    )

