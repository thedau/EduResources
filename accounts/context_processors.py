"""
Context processors cho ứng dụng Tài khoản.
Cung cấp thông tin vai trò người dùng cho tất cả template.
"""

from django.core.cache import cache
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
        # Số tài liệu chờ duyệt (cho Admin hiển thị badge) - cached 60s
        if request.user.is_admin:
            pending = cache.get('pending_resources_count')
            if pending is None:
                pending = Resource.objects.filter(status='pending').count()
                cache.set('pending_resources_count', pending, 60)
            context['pending_count'] = pending

    return context
