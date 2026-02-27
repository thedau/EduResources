"""
Cấu hình URL chính cho dự án EduResource.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from eduresource.views import home

urlpatterns = [
    # Trang chủ
    path('', home, name='home'),
    # Quản trị Django
    path('admin/', admin.site.urls),
    # Ứng dụng
    path('accounts/', include('accounts.urls')),
    path('resources/', include('resources.urls')),
    path('categories/', include('categories.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('notifications.urls')),
]

# Phục vụ tệp media trong chế độ phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
