"""
Mô hình Người dùng tùy chỉnh cho EduResource.
Hỗ trợ phân quyền theo vai trò: Khách, Người dùng, Quản trị viên.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Mô hình người dùng tùy chỉnh với vai trò và thông tin cá nhân.
    Kế thừa từ AbstractUser của Django để tận dụng hệ thống xác thực có sẵn.
    """

    class Role(models.TextChoices):
        """Các vai trò người dùng trong hệ thống."""
        GUEST = 'guest', 'Khách'
        USER = 'user', 'Người dùng'
        ADMIN = 'admin', 'Quản trị viên'

    # Thông tin cá nhân mở rộng
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Vai trò'
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name='Họ và tên',
        blank=True
    )
    phone = models.CharField(
        max_length=15,
        verbose_name='Số điện thoại',
        blank=True
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='Ảnh đại diện',
        blank=True,
        null=True
    )
    bio = models.TextField(
        verbose_name='Giới thiệu bản thân',
        blank=True
    )

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['-date_joined']

    def __str__(self):
        return self.full_name or self.username

    @property
    def is_admin(self):
        """Kiểm tra người dùng có phải quản trị viên không."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_user(self):
        """Kiểm tra người dùng có phải người dùng thường không."""
        return self.role == self.Role.USER

    @property
    def is_guest(self):
        """Kiểm tra người dùng có phải khách không."""
        return self.role == self.Role.GUEST

    @property
    def display_role(self):
        """Lấy tên hiển thị của vai trò."""
        return dict(self.Role.choices).get(self.role, 'Không xác định')
