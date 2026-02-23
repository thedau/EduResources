"""
Forms cho ứng dụng Danh mục.
"""

from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    """Form tạo và chỉnh sửa danh mục."""

    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên danh mục'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mô tả về danh mục',
                'rows': 3
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: fas fa-book'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Tên danh mục',
            'description': 'Mô tả',
            'icon': 'Biểu tượng (Font Awesome)',
            'parent': 'Danh mục cha',
            'is_active': 'Đang hoạt động',
        }

    def __init__(self, *args, **kwargs):
        """Loại bỏ chính danh mục hiện tại khỏi danh sách danh mục cha."""
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = '— Không có danh mục cha —'
