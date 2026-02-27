"""
View trang chủ cho dự án EduResource.
"""

from django.shortcuts import render
from django.db.models import Sum, Count, Q, Avg
from resources.models import Resource
from categories.models import Category
from accounts.models import User


def home(request):
    """Hiển thị trang chủ với danh mục, tài liệu nổi bật và thống kê."""
    # Lấy danh mục với số lượng tài liệu
    categories = Category.objects.filter(is_active=True).annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).order_by('-resource_count')[:8]

    # Base queryset cho tài liệu đã duyệt (annotated)
    approved_base = Resource.objects.filter(
        status='approved'
    ).select_related('category', 'author').annotate(
        avg_rating=Avg('comments__rating'),
        num_comments=Count('comments'),
    )

    # Tài liệu mới nhất đã duyệt
    recent_resources = approved_base.order_by('-created_at')[:6]

    # Tài liệu phổ biến nhất
    popular_resources = approved_base.order_by('-view_count')[:6]

    # Thống kê tổng quan - 1 query tổng hợp thay vì nhiều query riêng lẻ
    resource_stats = Resource.objects.filter(status='approved').aggregate(
        total=Count('id'),
        total_downloads=Sum('download_count'),
    )

    stats = {
        'total_resources': resource_stats['total'],
        'total_users': User.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_downloads': resource_stats['total_downloads'] or 0,
    }

    context = {
        'categories': categories,
        'recent_resources': recent_resources,
        'popular_resources': popular_resources,
        'stats': stats,
    }
    return render(request, 'home.html', context)
