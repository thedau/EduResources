"""
Mô hình Tài liệu, Bình luận và Nhật ký duyệt cho EduResource.
Bao gồm: Resource, Comment, SubmissionLog.
"""

import io
import mimetypes
import os

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import default_storage
from unidecode import unidecode
from categories.models import Category

try:
    from cloudinary_storage.storage import RawMediaCloudinaryStorage
except Exception:
    RawMediaCloudinaryStorage = None

try:
    from cloudinary.utils import cloudinary_url
except Exception:
    cloudinary_url = None


RESOURCE_FILE_STORAGE = (
    RawMediaCloudinaryStorage()
    if getattr(settings, 'CLOUDINARY_URL', '') and RawMediaCloudinaryStorage
    else default_storage
)


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
        storage=RESOURCE_FILE_STORAGE,
        help_text='Cho phép: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, ZIP, RAR (tối đa 10MB)'
    )
    file_blob = models.BinaryField(
        verbose_name='Nội dung tệp (DB)',
        blank=True,
        null=True,
        editable=False,
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='Tên tệp gốc',
        blank=True,
        default='',
    )
    file_content_type = models.CharField(
        max_length=120,
        verbose_name='MIME type của tệp',
        blank=True,
        default='',
    )
    file_size = models.PositiveBigIntegerField(
        verbose_name='Kích thước tệp (bytes)',
        default=0,
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
        indexes = [
            models.Index(fields=['status', '-created_at'], name='idx_resource_status_created'),
            models.Index(fields=['status', '-view_count'], name='idx_resource_status_views'),
            models.Index(fields=['status', '-download_count'], name='idx_resource_status_downloads'),
            models.Index(fields=['category', 'status'], name='idx_resource_category_status'),
            models.Index(fields=['author', '-created_at'], name='idx_resource_author_created'),
            models.Index(fields=['slug'], name='idx_resource_slug'),
        ]

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
        filename = self.file_basename
        if filename:
            return os.path.splitext(filename)[1].lower()
        return ''

    @property
    def has_file_attachment(self):
        """Kiểm tra tài liệu có tệp đính kèm (storage hoặc DB)."""
        return bool(self.file) or bool(self.file_blob)

    @property
    def file_basename(self):
        """Lấy tên file hiển thị ưu tiên theo tên gốc người dùng tải lên."""
        if self.file_name:
            return os.path.basename(self.file_name)
        if self.file:
            return os.path.basename(self.file.name)
        return ''

    def get_file_stream(self):
        """Mở stream đọc tệp từ storage; fallback sang dữ liệu trong DB nếu có."""
        if self.file:
            try:
                return self.file.open('rb')
            except Exception:
                # Fallback khi file vật lý bị mất ở môi trường deploy không persistent.
                pass
        if self.file_blob:
            return io.BytesIO(self.file_blob)
        return None

    def get_thumbnail_url(self):
        """Lấy URL ảnh thu nhỏ, ký URL nếu Cloudinary yêu cầu."""
        if not self.thumbnail:
            return ''
        url = getattr(self.thumbnail, 'url', '')
        if not url:
            return ''
        if not cloudinary_url:
            return url
        delivery_type = 'authenticated' if '/authenticated/' in url else 'upload'
        signed_url, _ = cloudinary_url(
            getattr(self.thumbnail, 'name', ''),
            resource_type='image',
            type=delivery_type,
            sign_url=(delivery_type == 'authenticated'),
            secure=True,
        )
        return signed_url or url

    @property
    def thumbnail_url(self):
        return self.get_thumbnail_url()

    def get_file_content_type(self):
        """Lấy MIME type đã lưu hoặc đoán từ tên tệp."""
        if self.file_content_type:
            return self.file_content_type
        guessed, _ = mimetypes.guess_type(self.file_basename)
        return guessed or 'application/octet-stream'

    @property
    def file_size_display(self):
        """Hiển thị kích thước tệp dạng đọc được."""
        size = 0
        if self.file_size:
            size = self.file_size
        elif self.file:
            try:
                size = self.file.size
            except Exception:
                size = 0

        if size > 0:
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
        indexes = [
            models.Index(fields=['resource', '-created_at'], name='idx_comment_resource_created'),
        ]

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
        indexes = [
            models.Index(fields=['resource', '-created_at'], name='idx_log_resource_created'),
        ]

    def __str__(self):
        return f"{self.resource} | {self.get_old_status_display()} → {self.get_new_status_display()}"


class Favorite(models.Model):
    """Tài liệu yêu thích của người dùng."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_resources',
        verbose_name='Người dùng'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Tài liệu'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )

    class Meta:
        verbose_name = 'Tài liệu yêu thích'
        verbose_name_plural = 'Tài liệu yêu thích'
        db_table = 'resources_favorite'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'resource'],
                name='unique_user_resource_favorite'
            )
        ]
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_favorite_user_created'),
            models.Index(fields=['resource'], name='idx_favorite_resource'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} ♥ {self.resource}"
