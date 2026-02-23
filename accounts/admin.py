"""Cấu hình Django Admin cho mô hình Người dùng."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


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
