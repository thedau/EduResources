"""
Context processors cho ứng dụng Tài khoản.
Cung cấp thông tin vai trò người dùng cho tất cả template.
"""

from resources.models import Resource


def user_role(request):
    """
    Context processor cung cấp thông tin vai trò và thống kê nhanh
    cho tất cả các template.
    """
    context = {
        'is_admin': False,
        'is_user': False,
        'user_role': 'guest',
        'pending_count': 0,
    }

    if request.user.is_authenticated:
        context.update({
            'is_admin': request.user.is_admin,
            'is_user': request.user.is_user,
            'user_role': request.user.role,
        })
        # Số tài liệu chờ duyệt (cho Admin hiển thị badge)
        if request.user.is_admin:
            context['pending_count'] = Resource.objects.filter(status='pending').count()

    return context
