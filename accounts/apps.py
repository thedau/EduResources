from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Cấu hình ứng dụng Tài khoản."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Quản lý tài khoản'
