"""Cấu hình Django Admin cho mô hình Người dùng."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Cấu hình hiển thị Người dùng trong trang quản trị."""

    list_display = ['username', 'full_name', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'full_name', 'email']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin mở rộng', {
            'fields': ('full_name', 'phone', 'avatar', 'bio', 'role')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin mở rộng', {
            'fields': ('full_name', 'email', 'role')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'actor', 'target_type', 'target_id', 'ip_address', 'created_at']
    list_filter = ['action', 'target_type', 'created_at']
    search_fields = ['action', 'target_type', 'target_id', 'actor__username']
    ordering = ['-created_at']
