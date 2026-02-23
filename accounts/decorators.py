"""
Decorators cho kiểm tra quyền truy cập.
Hỗ trợ phân quyền theo vai trò: Admin, Người dùng.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator yêu cầu người dùng phải là Admin.
    Chuyển hướng về trang chủ nếu không đủ quyền.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để tiếp tục.')
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def authenticated_required(view_func):
    """
    Decorator yêu cầu người dùng phải đăng nhập.
    Chuyển hướng đến trang đăng nhập nếu chưa đăng nhập.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Vui lòng đăng nhập để tiếp tục.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper
