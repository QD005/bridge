from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'agency', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'agency']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'username')}),
        ('Agency & Role', {'fields': ('agency', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at', 'last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'agency', 'role', 'password1', 'password2'),
        }),
    )

    ordering = ['-created_at']