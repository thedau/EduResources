from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    """Cấu hình ứng dụng Tài liệu."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resources'
    verbose_name = 'Quản lý tài liệu'
