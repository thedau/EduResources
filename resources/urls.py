"""URL patterns cho ứng dụng Tài liệu."""

from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Danh sách và CRUD
    path('', views.resource_list, name='list'),
    path('create/', views.resource_create, name='create'),
    path('my/', views.my_resources, name='my_resources'),
    path('favorites/', views.my_favorites, name='favorites'),
    path('pending/', views.pending_resources, name='pending'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<slug:slug>/', views.resource_detail, name='detail'),
    path('<slug:slug>/edit/', views.resource_edit, name='edit'),
    path('<slug:slug>/delete/', views.resource_delete, name='delete'),
    path('<slug:slug>/download/', views.download_resource, name='download'),
    path('<slug:slug>/preview/', views.preview_resource, name='preview'),
    path('<slug:slug>/file/', views.serve_file_inline, name='serve_file'),

    # Bình luận
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Duyệt tài liệu (Admin)
    path('<int:pk>/approve/', views.approve_resource, name='approve'),
    path('<int:pk>/reject/', views.reject_resource, name='reject'),
]
