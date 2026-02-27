"""
Signals cho ứng dụng Thông báo.
Tự động tạo thông báo khi có các sự kiện quan trọng.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from resources.models import SubmissionLog, Comment
from accounts.models import User
from .models import Notification


@receiver(post_save, sender=SubmissionLog)
def notify_on_status_change(sender, instance, created, **kwargs):
    """
    Tạo thông báo khi trạng thái tài liệu thay đổi.
    - Duyệt/Từ chối → thông báo cho tác giả
    - Chờ duyệt mới → thông báo cho tất cả admin
    """
    if not created:
        return

    resource = instance.resource
    resource_url = reverse('resources:detail', kwargs={'slug': resource.slug})

    # Tài liệu được duyệt → thông báo cho tác giả
    if instance.new_status == 'approved':
        Notification.objects.create(
            recipient=resource.author,
            notification_type=Notification.Type.RESOURCE_APPROVED,
            title='Tài liệu đã được duyệt',
            message=f'Tài liệu "{resource.title}" của bạn đã được phê duyệt.',
            link=resource_url,
        )

    # Tài liệu bị từ chối → thông báo cho tác giả
    elif instance.new_status == 'rejected':
        reason = instance.note or 'Không có lý do cụ thể'
        Notification.objects.create(
            recipient=resource.author,
            notification_type=Notification.Type.RESOURCE_REJECTED,
            title='Tài liệu bị từ chối',
            message=f'Tài liệu "{resource.title}" bị từ chối. Lý do: {reason}',
            link=resource_url,
        )

    # Tài liệu mới chờ duyệt → thông báo cho tất cả admin
    elif instance.new_status == 'pending':
        pending_url = reverse('resources:pending')
        admins = User.objects.filter(role=User.Role.ADMIN, is_active=True)
        notifications = [
            Notification(
                recipient=admin,
                notification_type=Notification.Type.NEW_PENDING,
                title='Tài liệu mới chờ duyệt',
                message=f'"{resource.title}" bởi {resource.author.full_name or resource.author.username}',
                link=pending_url,
            )
            for admin in admins
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)


@receiver(post_save, sender=Comment)
def notify_on_new_comment(sender, instance, created, **kwargs):
    """
    Tạo thông báo khi có bình luận mới trên tài liệu.
    Thông báo cho tác giả tài liệu (không tự thông báo cho chính mình).
    """
    if not created:
        return

    resource = instance.resource
    commenter = instance.user

    # Không thông báo nếu tác giả tự comment
    if resource.author == commenter:
        return

    resource_url = reverse('resources:detail', kwargs={'slug': resource.slug})
    commenter_name = commenter.full_name or commenter.username

    Notification.objects.create(
        recipient=resource.author,
        notification_type=Notification.Type.NEW_COMMENT,
        title='Bình luận mới',
        message=f'{commenter_name} đã bình luận về "{resource.title}" ({instance.rating}⭐)',
        link=resource_url,
    )
