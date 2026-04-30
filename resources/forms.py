import os
import mimetypes

"""
Forms cho ứng dụng Tài liệu.
Bao gồm: Form tài liệu, Form bình luận, kiểm tra tệp tải lên.
"""

from django import forms
from django.conf import settings
from PIL import Image
from .models import Resource, Comment

ALLOWED_FILE_MIME_TYPES = {
    '.pdf': {'application/pdf'},
    '.doc': {'application/msword'},
    '.docx': {'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    '.ppt': {'application/vnd.ms-powerpoint'},
    '.pptx': {'application/vnd.openxmlformats-officedocument.presentationml.presentation'},
    '.xls': {'application/vnd.ms-excel'},
    '.xlsx': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    '.zip': {'application/zip', 'application/x-zip-compressed'},
    '.rar': {'application/vnd.rar', 'application/x-rar-compressed'},
}

ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
}


class ResourceForm(forms.ModelForm):
    """Form tạo và chỉnh sửa tài liệu."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_file = getattr(self.instance, 'file', None)
        self._original_thumbnail = getattr(self.instance, 'thumbnail', None)
        self.fields['file'].required = False
        self.fields['thumbnail'].required = False

    class Meta:
        model = Resource
        fields = [
            'title', 'description', 'content', 'resource_type',
            'category', 'file', 'thumbnail'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề tài liệu'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mô tả ngắn gọn về tài liệu',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nội dung chi tiết hoặc ghi chú về tài liệu',
                'rows': 8
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.rar'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': 'Tiêu đề',
            'description': 'Mô tả ngắn',
            'content': 'Nội dung chi tiết',
            'resource_type': 'Loại tài liệu',
            'category': 'Danh mục',
            'file': 'Tệp đính kèm',
            'thumbnail': 'Ảnh thu nhỏ',
        }

    def clean_file(self):
        """Kiểm tra tệp đính kèm: định dạng và kích thước."""
        file = self.cleaned_data.get('file')
        if file:
            # Kiểm tra kích thước tệp
            max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
            if file.size > max_size:
                raise forms.ValidationError(
                    f'Kích thước tệp vượt quá {max_size // (1024 * 1024)}MB.'
                )
            # Kiểm tra phần mở rộng
            ext = os.path.splitext(file.name)[1].lower()
            allowed_exts = getattr(
                settings, 'ALLOWED_UPLOAD_EXTENSIONS',
                ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.zip', '.rar']
            )
            if ext not in allowed_exts:
                raise forms.ValidationError(
                    f'Định dạng tệp không được hỗ trợ. Cho phép: {", ".join(allowed_exts)}'
                )
            declared_type = file.content_type or (mimetypes.guess_type(file.name)[0] or '')
            allowed_mimes = ALLOWED_FILE_MIME_TYPES.get(ext, set())
            if declared_type and allowed_mimes and declared_type not in allowed_mimes:
                raise forms.ValidationError('MIME type của tệp không hợp lệ so với phần mở rộng.')
        return file

    def clean_thumbnail(self):
        """Kiểm tra ảnh thu nhỏ: định dạng và kích thước."""
        image = self.cleaned_data.get('thumbnail')
        if image:
            # Kiểm tra kích thước
            max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
            if image.size > max_size:
                raise forms.ValidationError(
                    f'Kích thước ảnh vượt quá {max_size // (1024 * 1024)}MB.'
                )
            # Kiểm tra phần mở rộng
            ext = os.path.splitext(image.name)[1].lower()
            allowed_exts = getattr(
                settings, 'ALLOWED_IMAGE_EXTENSIONS',
                ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            )
            if ext not in allowed_exts:
                raise forms.ValidationError(
                    f'Định dạng ảnh không được hỗ trợ. Cho phép: {", ".join(allowed_exts)}'
                )
            declared_type = image.content_type or (mimetypes.guess_type(image.name)[0] or '')
            if declared_type and declared_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise forms.ValidationError('MIME type của ảnh không hợp lệ.')
            try:
                img = Image.open(image)
                img.verify()
            except Exception:
                raise forms.ValidationError('Ảnh không hợp lệ hoặc bị hỏng.')
            finally:
                try:
                    image.seek(0)
                except Exception:
                    pass
        return image

    def save(self, commit=True):
        """Lưu tài liệu và đồng bộ dữ liệu file vào DB khi được bật qua settings."""
        instance = super().save(commit=False)
        uploaded_file = self.cleaned_data.get('file')
        uploaded_thumbnail = self.cleaned_data.get('thumbnail')

        if not uploaded_file and self._original_file:
            instance.file = self._original_file

        if not uploaded_thumbnail and self._original_thumbnail:
            instance.thumbnail = self._original_thumbnail

        if uploaded_file:
            instance.file_name = uploaded_file.name
            instance.file_content_type = uploaded_file.content_type or (
                mimetypes.guess_type(uploaded_file.name)[0] or 'application/octet-stream'
            )
            instance.file_size = uploaded_file.size or 0

            if getattr(settings, 'STORE_UPLOADS_IN_DB', False):
                file_bytes = uploaded_file.read()
                uploaded_file.seek(0)
                instance.file_blob = file_bytes
        elif not instance.file:
            # Nếu bỏ tệp hiện tại, xóa metadata liên quan.
            instance.file_blob = None
            instance.file_name = ''
            instance.file_content_type = ''
            instance.file_size = 0

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CommentForm(forms.ModelForm):
    """Form thêm bình luận và đánh giá."""

    class Meta:
        model = Comment
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Viết bình luận của bạn...',
                'rows': 3
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'value': 5
            }),
        }
        labels = {
            'content': 'Nội dung bình luận',
            'rating': 'Đánh giá (1-5 sao)',
        }


class ResourceRejectForm(forms.Form):
    """Form từ chối tài liệu (Admin)."""

    rejection_reason = forms.CharField(
        label='Lý do từ chối',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lý do từ chối tài liệu...',
            'rows': 3
        }),
        required=True
    )
