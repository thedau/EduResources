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
    path('', include('ai_features.urls')),
]

# Phục vụ tệp media khi DEBUG hoặc được bật rõ ràng
if settings.DEBUG or getattr(settings, "SERVE_MEDIA", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler403 = 'eduresource.views.custom_403'
handler404 = 'eduresource.views.custom_404'
handler500 = 'eduresource.views.custom_500'
