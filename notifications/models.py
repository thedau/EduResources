"""
Mô hình Thông báo cho EduResource.
Hỗ trợ thông báo real-time qua AJAX polling.
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Thông báo cho người dùng.
    Tự động tạo khi: tài liệu được duyệt/từ chối, có comment mới,
    có tài liệu mới chờ duyệt (cho admin).
    """

    class Type(models.TextChoices):
        RESOURCE_APPROVED = 'resource_approved', 'Tài liệu được duyệt'
        RESOURCE_REJECTED = 'resource_rejected', 'Tài liệu bị từ chối'
        NEW_COMMENT = 'new_comment', 'Bình luận mới'
        NEW_PENDING = 'new_pending', 'Tài liệu chờ duyệt'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Người nhận'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name='Loại thông báo'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Tiêu đề'
    )
    message = models.TextField(
        verbose_name='Nội dung',
        blank=True
    )
    link = models.CharField(
        max_length=500,
        verbose_name='Đường dẫn',
        blank=True,
        help_text='URL để chuyển đến khi click thông báo'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Đã đọc'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Thời gian'
    )

    class Meta:
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at'],
                         name='idx_notif_recipient_unread'),
            models.Index(fields=['recipient', '-created_at'],
                         name='idx_notif_recipient_created'),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} → {self.recipient}"

    @property
    def icon_class(self):
        """Lấy class icon Font Awesome theo loại thông báo."""
        return {
            'resource_approved': 'fas fa-check-circle text-success',
            'resource_rejected': 'fas fa-times-circle text-danger',
            'new_comment': 'fas fa-comment text-info',
            'new_pending': 'fas fa-clock text-warning',
        }.get(self.notification_type, 'fas fa-bell text-primary')


class UserActivity(models.Model):
    """
    Theo dõi hoạt động người dùng để hiển thị số người đang online.
    Cập nhật mỗi khi người dùng gửi request.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity',
        verbose_name='Người dùng'
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        verbose_name='Lần cuối hoạt động'
    )

    class Meta:
        verbose_name = 'Hoạt động người dùng'
        verbose_name_plural = 'Hoạt động người dùng'

    def __str__(self):
        return f"{self.user} - {self.last_seen}"
