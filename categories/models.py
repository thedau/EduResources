"""
Mô hình Danh mục tài liệu cho EduResource.
Hỗ trợ phân cấp danh mục (danh mục cha - con).
"""

from django.db import models
from django.utils.text import slugify
from unidecode import unidecode


class Category(models.Model):
    """
    Danh mục phân loại tài liệu học tập.
    Hỗ trợ cấu trúc cây với danh mục cha - con.
    """

    name = models.CharField(
        max_length=100,
        verbose_name='Tên danh mục',
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Đường dẫn'
    )
    description = models.TextField(
        verbose_name='Mô tả',
        blank=True
    )
    icon = models.CharField(
        max_length=50,
        verbose_name='Biểu tượng (Font Awesome)',
        default='fas fa-folder',
        help_text='Ví dụ: fas fa-book, fas fa-flask, fas fa-calculator'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Danh mục cha'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
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
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Tự động tạo slug từ tên danh mục nếu chưa có."""
        if not self.slug:
            base_slug = slugify(unidecode(self.name))
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def approved_resource_count(self):
        """Đếm số tài liệu đã duyệt trong danh mục."""
        return self.resources.filter(status='approved').count()
