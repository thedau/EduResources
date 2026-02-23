"""
View trang chủ cho dự án EduResource.
"""

from django.shortcuts import render
from django.db.models import Sum, Count
from resources.models import Resource
from categories.models import Category
from accounts.models import User


def home(request):
    """Hiển thị trang chủ với danh mục, tài liệu nổi bật và thống kê."""
    # Lấy danh mục với số lượng tài liệu
    categories = Category.objects.annotate(
        resource_count=Count('resources', filter=models.Q(resources__status='approved'))
    ).order_by('-resource_count')[:8]

    # Tài liệu mới nhất đã duyệt
    recent_resources = Resource.objects.filter(
        status='approved'
    ).select_related('category', 'author').order_by('-created_at')[:6]

    # Tài liệu phổ biến nhất
    popular_resources = Resource.objects.filter(
        status='approved'
    ).select_related('category', 'author').order_by('-view_count')[:6]

    # Thống kê tổng quan
    stats = {
        'total_resources': Resource.objects.filter(status='approved').count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.count(),
        'total_downloads': Resource.objects.aggregate(
            total=Sum('download_count')
        )['total'] or 0,
    }

    context = {
        'categories': categories,
        'recent_resources': recent_resources,
        'popular_resources': popular_resources,
        'stats': stats,
    }
    return render(request, 'home.html', context)


# Import models cho annotation
from django.db import models
