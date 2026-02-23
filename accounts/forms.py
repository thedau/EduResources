"""
Forms cho ứng dụng Tài khoản.
Bao gồm: Đăng ký, Đăng nhập, Cập nhật hồ sơ, Quản lý vai trò.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    """Form đăng ký tài khoản mới."""

    full_name = forms.CharField(
        max_length=150,
        label='Họ và tên',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ và tên'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ email'
        })
    )
    username = forms.CharField(
        label='Tên đăng nhập',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập'
        })
    )
    password1 = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu (ít nhất 6 ký tự)'
        })
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        """Kiểm tra email đã tồn tại chưa."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email


class LoginForm(AuthenticationForm):
    """Form đăng nhập."""

    username = forms.CharField(
        label='Tên đăng nhập',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu'
        })
    )

    error_messages = {
        'invalid_login': 'Tên đăng nhập hoặc mật khẩu không đúng.',
        'inactive': 'Tài khoản này đã bị vô hiệu hóa.',
    }


class ProfileForm(forms.ModelForm):
    """Form cập nhật hồ sơ cá nhân."""

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'bio', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ và tên'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Giới thiệu về bản thân',
                'rows': 4
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'full_name': 'Họ và tên',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'bio': 'Giới thiệu',
            'avatar': 'Ảnh đại diện',
        }


class UserRoleForm(forms.ModelForm):
    """Form cập nhật vai trò người dùng (dành cho Admin)."""

    class Meta:
        model = User
        fields = ['role', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'role': 'Vai trò',
            'is_active': 'Đang hoạt động',
        }


class ForgotPasswordForm(forms.Form):
    """Form quên mật khẩu - nhập email để nhận link đặt lại."""

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email đã đăng ký'
        })
    )


class ResetPasswordForm(forms.Form):
    """Form đặt lại mật khẩu."""

    password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới (ít nhất 6 ký tự)'
        }),
        min_length=6
    )
    password_confirm = forms.CharField(
        label='Xác nhận mật khẩu mới',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu mới'
        })
    )

    def clean(self):
        """Kiểm tra hai mật khẩu có khớp nhau không."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Mật khẩu không khớp.')
        return cleaned_data
