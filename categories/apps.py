from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    """Cấu hình ứng dụng Danh mục."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'categories'
    verbose_name = 'Quản lý danh mục'
