"""Cấu hình ứng dụng AI Features."""

from django.apps import AppConfig


class AiFeaturesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_features'
    verbose_name = 'Tính năng AI'
