"""
Mô hình Tài liệu, Bình luận và Nhật ký duyệt cho EduResource.
Bao gồm: Resource, Comment, SubmissionLog.
"""

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from unidecode import unidecode
from categories.models import Category
import os


class Resource(models.Model):
    """
    Mô hình tài liệu học tập.
    Hỗ trợ quy trình duyệt: Chờ duyệt → Đã duyệt / Từ chối.
    """

    class Status(models.TextChoices):
        """Trạng thái duyệt tài liệu."""
        PENDING = 'pending', 'Chờ duyệt'
        APPROVED = 'approved', 'Đã duyệt'
        REJECTED = 'rejected', 'Từ chối'

    class ResourceType(models.TextChoices):
        """Loại tài liệu."""
        DOCUMENT = 'document', 'Tài liệu'
        VIDEO = 'video', 'Video'
        PRESENTATION = 'presentation', 'Bài trình bày'
        EXERCISE = 'exercise', 'Bài tập'
        OTHER = 'other', 'Khác'

    # Thông tin cơ bản
    title = models.CharField(
        max_length=255,
        verbose_name='Tiêu đề'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Đường dẫn'
    )
    description = models.TextField(
        verbose_name='Mô tả ngắn',
        blank=True,
        help_text='Mô tả tóm tắt nội dung tài liệu'
    )
    content = models.TextField(
        verbose_name='Nội dung chi tiết',
        blank=True,
        help_text='Nội dung đầy đủ hoặc ghi chú về tài liệu'
    )
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.DOCUMENT,
        verbose_name='Loại tài liệu'
    )

    # Quan hệ
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Danh mục'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Tác giả'
    )

    # Tệp đính kèm
    file = models.FileField(
        upload_to='resources/files/%Y/%m/',
        verbose_name='Tệp đính kèm',
        blank=True,
        null=True,
        help_text='Cho phép: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, ZIP, RAR (tối đa 10MB)'
    )
    thumbnail = models.ImageField(
        upload_to='resources/thumbnails/%Y/%m/',
        verbose_name='Ảnh thu nhỏ',
        blank=True,
        null=True,
        help_text='Cho phép: JPG, PNG, GIF, WEBP (tối đa 10MB)'
    )

    # Trạng thái duyệt
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Trạng thái'
    )
    rejection_reason = models.TextField(
        verbose_name='Lý do từ chối',
        blank=True
    )

    # Thống kê
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Lượt xem'
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Lượt tải xuống'
    )

    # Dấu thời gian
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    class Meta:
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Tự động tạo slug từ tiêu đề nếu chưa có."""
        if not self.slug:
            base_slug = slugify(unidecode(self.title))
            if not base_slug:
                base_slug = 'tai-lieu'
            slug = base_slug
            counter = 1
            while Resource.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        """Lấy phần mở rộng của tệp đính kèm."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''

    @property
    def file_size_display(self):
        """Hiển thị kích thước tệp dạng đọc được."""
        if self.file and self.file.size:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return ''

    @property
    def average_rating(self):
        """Tính điểm đánh giá trung bình."""
        avg = self.comments.aggregate(avg=models.Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    @property
    def comment_count(self):
        """Đếm số bình luận."""
        return self.comments.count()

    @property
    def status_badge_class(self):
        """Lấy class CSS cho badge trạng thái."""
        return {
            'pending': 'bg-warning text-dark',
            'approved': 'bg-success',
            'rejected': 'bg-danger',
        }.get(self.status, 'bg-secondary')


class Comment(models.Model):
    """
    Bình luận và đánh giá cho tài liệu.
    Mỗi bình luận kèm theo điểm đánh giá từ 1-5 sao.
    """

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Tài liệu'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Người bình luận'
    )
    content = models.TextField(
        verbose_name='Nội dung bình luận'
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Đánh giá (1-5 sao)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    class Meta:
        verbose_name = 'Bình luận'
        verbose_name_plural = 'Bình luận'
        ordering = ['-created_at']

    def __str__(self):
        return f"Bình luận của {self.user} về {self.resource}"


class SubmissionLog(models.Model):
    """
    Nhật ký theo dõi quy trình duyệt tài liệu.
    Ghi lại mỗi lần thay đổi trạng thái của tài liệu.
    """

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='submission_logs',
        verbose_name='Tài liệu'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewed_submissions',
        verbose_name='Người duyệt'
    )
    old_status = models.CharField(
        max_length=10,
        choices=Resource.Status.choices,
        verbose_name='Trạng thái cũ'
    )
    new_status = models.CharField(
        max_length=10,
        choices=Resource.Status.choices,
        verbose_name='Trạng thái mới'
    )
    note = models.TextField(
        verbose_name='Ghi chú',
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Thời gian'
    )

    class Meta:
        verbose_name = 'Nhật ký duyệt'
        verbose_name_plural = 'Nhật ký duyệt'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.resource} | {self.get_old_status_display()} → {self.get_new_status_display()}"
