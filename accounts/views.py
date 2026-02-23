"""
Views cho ứng dụng Tài khoản.
Xử lý: Đăng ký, Đăng nhập, Đăng xuất, Hồ sơ, Quên mật khẩu, Quản lý người dùng.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User
from .forms import RegisterForm, LoginForm, ProfileForm, UserRoleForm, ForgotPasswordForm, ResetPasswordForm
from .decorators import admin_required


def register(request):
    """Xử lý đăng ký tài khoản mới."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.USER
            user.save()
            # Tự động đăng nhập sau khi đăng ký
            login(request, user)
            messages.success(request, f'Chào mừng {user.full_name}! Tài khoản đã được tạo thành công.')
            return redirect('home')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin đăng ký.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Xử lý đăng nhập."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Chào mừng {user.full_name or user.username} quay lại!')
            # Chuyển hướng đến trang trước đó nếu có
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Xử lý đăng xuất."""
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công.')
    return redirect('home')


@login_required
def profile(request):
    """Xem và cập nhật hồ sơ cá nhân."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hồ sơ đã được cập nhật thành công.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = ProfileForm(instance=request.user)

    # Thống kê cá nhân
    user_stats = {
        'total_resources': request.user.resources.count(),
        'approved_resources': request.user.resources.filter(status='approved').count(),
        'pending_resources': request.user.resources.filter(status='pending').count(),
        'total_comments': request.user.comments.count(),
    }

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user_stats': user_stats,
    })


def forgot_password(request):
    """Xử lý quên mật khẩu - tạo link đặt lại mật khẩu."""
    if request.user.is_authenticated:
        return redirect('home')

    reset_url = None

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Tạo token đặt lại mật khẩu
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(
                    f'/accounts/reset-password/{uid}/{token}/'
                )
                messages.success(
                    request,
                    'Link đặt lại mật khẩu đã được tạo. Vui lòng sử dụng link bên dưới.'
                )
            except User.DoesNotExist:
                messages.error(request, 'Không tìm thấy tài khoản với email này.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {
        'form': form,
        'reset_url': reset_url,
    })


def reset_password(request, uidb64, token):
    """Xử lý đặt lại mật khẩu bằng token."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()
                messages.success(request, 'Mật khẩu đã được đặt lại thành công. Vui lòng đăng nhập.')
                return redirect('accounts:login')
        else:
            form = ResetPasswordForm()
        return render(request, 'accounts/reset_password.html', {'form': form})
    else:
        messages.error(request, 'Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.')
        return redirect('accounts:forgot_password')


@admin_required
def manage_users(request):
    """Quản lý người dùng - chỉ dành cho Admin."""
    search_query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    users = User.objects.all()

    # Tìm kiếm
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Lọc theo vai trò
    if role_filter:
        users = users.filter(role=role_filter)

    # Phân trang
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/manage_users.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': User.Role.choices,
    })


@admin_required
def update_user_role(request, user_id):
    """Cập nhật vai trò người dùng - chỉ dành cho Admin."""
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật vai trò cho {user.full_name or user.username}.')
        else:
            messages.error(request, 'Không thể cập nhật vai trò.')

    return redirect('accounts:manage_users')
