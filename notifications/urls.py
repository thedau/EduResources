"""URL patterns cho ứng dụng Thông báo."""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # API Thông báo real-time
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:pk>/read/', views.api_mark_read, name='api_mark_read'),
    path('api/notifications/read-all/', views.api_mark_all_read, name='api_mark_all_read'),

    # API Live Search
    path('api/search/', views.api_live_search, name='api_live_search'),

    # API Online Users
    path('api/online-users/', views.api_online_users, name='api_online_users'),

    # API Dashboard Stats
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
