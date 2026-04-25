"""
View trang chủ và error handlers cho dự án EduResource.
"""
import json
from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import Sum, Count, Q, Avg, Case, When, IntegerField
from django.utils import timezone
from resources.models import Resource
from categories.models import Category
from accounts.models import User


HOME_STATS_CACHE_KEY = "home_stats_v2"
HOME_MONTHLY_CHART_CACHE_KEY = "home_monthly_chart_v3"
HOME_CACHE_TTL = 300


def _ordered_case_by_ids(id_list):
    return Case(
        *[When(pk=pk, then=position) for position, pk in enumerate(id_list)],
        output_field=IntegerField(),
    )


def home(request):
    """Hiển thị trang chủ với danh mục, tài liệu nổi bật và thống kê."""
    # Lấy danh mục với số lượng tài liệu
    categories = Category.objects.filter(is_active=True).annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).order_by('-resource_count')[:8]

    approved_resources = Resource.objects.filter(status='approved')

    # Lấy ID trước, sau đó annotate trên tập nhỏ để giảm tải DB
    recent_ids = list(approved_resources.order_by('-created_at').values_list('id', flat=True)[:6])
    popular_ids = list(approved_resources.order_by('-view_count').values_list('id', flat=True)[:6])

    recent_resources = Resource.objects.none()
    if recent_ids:
        recent_resources = (
            Resource.objects.filter(pk__in=recent_ids)
            .select_related('category', 'author')
            .annotate(avg_rating=Avg('comments__rating'))
            .order_by(_ordered_case_by_ids(recent_ids))
        )

    popular_resources = Resource.objects.none()
    if popular_ids:
        popular_resources = (
            Resource.objects.filter(pk__in=popular_ids)
            .select_related('category', 'author')
            .annotate(avg_rating=Avg('comments__rating'))
            .order_by(_ordered_case_by_ids(popular_ids))
        )

    stats = cache.get(HOME_STATS_CACHE_KEY)
    if stats is None:
        resource_stats = approved_resources.aggregate(
            total=Count('id'),
            total_downloads=Sum('download_count'),
        )
        stats = {
            'total_resources': resource_stats['total'],
            'total_users': User.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_downloads': resource_stats['total_downloads'] or 0,
        }
        cache.set(HOME_STATS_CACHE_KEY, stats, HOME_CACHE_TTL)

    # Tài liệu theo tháng (6 tháng gần nhất)
    chart_monthly = cache.get(HOME_MONTHLY_CHART_CACHE_KEY)
    if chart_monthly is None:
        now = timezone.now()
        month_pairs = []
        for offset in range(5, -1, -1):
            month = now.month - offset
            year = now.year
            while month <= 0:
                month += 12
                year -= 1
            month_pairs.append((year, month))

        first_year, first_month = month_pairs[0]
        first_month_start = datetime(
            first_year,
            first_month,
            1,
            tzinfo=timezone.get_current_timezone(),
        )

        monthly_map = {(year, month): 0 for year, month in month_pairs}
        monthly_datetimes = approved_resources.filter(created_at__gte=first_month_start).values_list('created_at', flat=True)

        for created_at in monthly_datetimes:
            if created_at is None:
                continue
            local_dt = timezone.localtime(created_at) if timezone.is_aware(created_at) else created_at
            month_key = (local_dt.year, local_dt.month)
            if month_key in monthly_map:
                monthly_map[month_key] += 1

        chart_monthly = json.dumps(
            {
                'labels': [datetime(year, month, 1).strftime('%m/%Y') for year, month in month_pairs],
                'data': [monthly_map.get((year, month), 0) for year, month in month_pairs],
            },
            ensure_ascii=False,
        )
        cache.set(HOME_MONTHLY_CHART_CACHE_KEY, chart_monthly, HOME_CACHE_TTL)

    context = {
        'categories': categories,
        'recent_resources': recent_resources,
        'popular_resources': popular_resources,
        'stats': stats,
        'chart_monthly': chart_monthly,
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
