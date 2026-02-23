"""Cấu hình Django Admin cho mô hình Tài liệu, Bình luận, Nhật ký."""

from django.contrib import admin
from .models import Resource, Comment, SubmissionLog


class CommentInline(admin.TabularInline):
    """Hiển thị bình luận inline trong trang tài liệu."""
    model = Comment
    extra = 0
    readonly_fields = ['user', 'created_at']


class SubmissionLogInline(admin.TabularInline):
    """Hiển thị nhật ký duyệt inline trong trang tài liệu."""
    model = SubmissionLog
    extra = 0
    readonly_fields = ['reviewer', 'old_status', 'new_status', 'note', 'created_at']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Cấu hình hiển thị Tài liệu trong trang quản trị."""

    list_display = ['title', 'category', 'author', 'status', 'view_count', 'download_count', 'created_at']
    list_filter = ['status', 'resource_type', 'category', 'created_at']
    search_fields = ['title', 'description', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'download_count']
    ordering = ['-created_at']
    inlines = [CommentInline, SubmissionLogInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Cấu hình hiển thị Bình luận trong trang quản trị."""

    list_display = ['user', 'resource', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['content', 'user__username']
    ordering = ['-created_at']


@admin.register(SubmissionLog)
class SubmissionLogAdmin(admin.ModelAdmin):
    """Cấu hình hiển thị Nhật ký duyệt trong trang quản trị."""

    list_display = ['resource', 'reviewer', 'old_status', 'new_status', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['resource__title', 'note']
    ordering = ['-created_at']
