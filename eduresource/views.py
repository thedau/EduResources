"""
View trang chủ và error handlers cho dự án EduResource.
"""

from django.shortcuts import render
from django.http import JsonResponse
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


# === CUSTOM ERROR HANDLERS ===

def custom_403(request, exception=None):
    """Trang lỗi 403 - Truy cập bị từ chối."""
    return render(request, '403.html', status=403)


def custom_404(request, exception=None):
    """Trang lỗi 404 - Không tìm thấy trang."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Trang lỗi 500 - Lỗi máy chủ."""
    return render(request, '500.html', status=500)


def ratelimit_error(request, exception=None):
    """Xử lý khi bị rate limit - trả về 429."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {'success': False, 'error': 'Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.'},
            status=429
        )
    return render(request, '429.html', status=429)
