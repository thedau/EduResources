"""
Middleware cho ứng dụng Thông báo.
Theo dõi hoạt động người dùng để đếm số người đang online.
"""

from django.utils import timezone
from .models import UserActivity


class OnlineUsersMiddleware:
    """
    Middleware cập nhật last_seen của người dùng đã đăng nhập.
    Chỉ cập nhật mỗi 60 giây để tránh ghi DB quá nhiều.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            # Chỉ cập nhật mỗi 60 giây (dùng session để track)
            last_update = request.session.get('_last_activity_update', 0)
            now_ts = int(timezone.now().timestamp())

            if now_ts - last_update > 60:
                UserActivity.objects.update_or_create(
                    user=request.user,
                    defaults={'last_seen': timezone.now()}
                )
                request.session['_last_activity_update'] = now_ts

        return response
