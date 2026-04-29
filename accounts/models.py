"""
Mô hình Người dùng tùy chỉnh cho EduResource.
Hỗ trợ phân quyền theo vai trò: Khách, Người dùng, Quản trị viên.
"""

from django.contrib.auth.models import AbstractUser
from django.conf import settings
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


class AuditLog(models.Model):
    """Nhật ký hành động quan trọng để phục vụ kiểm toán."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Người thực hiện',
    )
    action = models.CharField(max_length=200, verbose_name='Hành động')
    target_type = models.CharField(max_length=100, blank=True, verbose_name='Loại đối tượng')
    target_id = models.CharField(max_length=64, blank=True, verbose_name='ID đối tượng')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Dữ liệu bổ sung')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')

    class Meta:
        verbose_name = 'Nhật ký kiểm toán'
        verbose_name_plural = 'Nhật ký kiểm toán'
        ordering = ['-created_at']

    def __str__(self):
        actor = self.actor.username if self.actor else 'System'
        return f"{actor} - {self.action}"


def create_audit_log(actor, action, target=None, metadata=None, ip_address=None):
    """Tạo audit log an toàn, tránh làm vỡ luồng xử lý chính."""
    try:
        target_type = ''
        target_id = ''
        if target is not None:
            target_type = target.__class__.__name__
            target_id = str(getattr(target, 'pk', '') or '')

        AuditLog.objects.create(
            actor=actor if getattr(actor, 'is_authenticated', False) else None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            metadata=metadata or {},
        )
    except Exception:
        # Không để lỗi audit ảnh hưởng luồng chính.
        pass
