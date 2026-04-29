"""
Views cho ứng dụng Thông báo.
Cung cấp API JSON cho: thông báo real-time, live search,
online users, live dashboard stats.
"""

from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .models import Notification, UserActivity
from resources.models import Resource, Comment
from categories.models import Category
from accounts.models import User
from accounts.decorators import admin_required


# ============================================================
# 1. REAL-TIME NOTIFICATIONS API
# ============================================================

@login_required
@ratelimit(key='user', rate='120/m', method='GET', block=True)
def api_notifications(request):
    """
    API trả về danh sách thông báo chưa đọc + số lượng.
    Được gọi bởi JS mỗi 15 giây.
    """
    cache_key = f"notifications:{request.user.pk}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    unread_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:20]

    data = {
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'link': n.link,
                'is_read': n.is_read,
                'icon_class': n.icon_class,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
                'time_ago': _time_ago(n.created_at),
            }
            for n in notifications
        ],
    }
    cache.set(cache_key, data, 10)
    return JsonResponse(data)


@login_required
@require_POST
def api_mark_read(request, pk):
    """Đánh dấu một thông báo đã đọc."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    cache.delete(f"notifications:{request.user.pk}")
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def api_mark_all_read(request):
    """Đánh dấu tất cả thông báo đã đọc."""
    Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    cache.delete(f"notifications:{request.user.pk}")
    return JsonResponse({'status': 'ok'})


# ============================================================
# 4. LIVE SEARCH API
# ============================================================

@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def api_live_search(request):
    """
    API tìm kiếm tức thì - trả về kết quả JSON.
    Được gọi khi người dùng gõ trong ô tìm kiếm (debounced 300ms).
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': [], 'total': 0})

    cache_key = f"live_search:{q.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    resources = Resource.objects.filter(
        status='approved'
    ).filter(
        Q(title__icontains=q) |
        Q(description__icontains=q)
    ).select_related('category', 'author').annotate(
        avg_rating=Avg('comments__rating'),
    ).order_by('-view_count')[:8]

    results = []
    for r in resources:
        results.append({
            'title': r.title,
            'slug': r.slug,
            'category': r.category.name,
            'author': r.author.full_name or r.author.username,
            'type': r.get_resource_type_display(),
            'type_raw': r.resource_type,
            'view_count': r.view_count,
            'rating': round(r.avg_rating, 1) if r.avg_rating else 0,
            'thumbnail': r.thumbnail.url if r.thumbnail else '',
            'created_at': r.created_at.strftime('%d/%m/%Y'),
        })

    total = Resource.objects.filter(
        status='approved'
    ).filter(
        Q(title__icontains=q) |
        Q(description__icontains=q)
    ).count()

    data = {
        'results': results,
        'total': total,
        'query': q,
    }
    cache.set(cache_key, data, 15)
    return JsonResponse(data)


# ============================================================
# 5. ONLINE USERS API
# ============================================================

def api_online_users(request):
    """
    API trả về số người đang online.
    Người dùng được coi là online nếu hoạt động trong 5 phút gần nhất.
    """
    cache_key = "online_users_count"
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse({'online_count': cached})

    threshold = timezone.now() - timedelta(minutes=5)
    online_count = UserActivity.objects.filter(last_seen__gte=threshold).count()
    cache.set(cache_key, online_count, 10)

    return JsonResponse({
        'online_count': online_count,
    })


# ============================================================
# 6. LIVE DASHBOARD STATS API
# ============================================================

@admin_required
def api_dashboard_stats(request):
    """
    API trả về thống kê dashboard real-time.
    Được gọi bởi JS mỗi 30 giây trên trang dashboard.
    """
    cache_key = "dashboard_stats"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    resource_agg = Resource.objects.aggregate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='approved')),
        pending=Count('id', filter=Q(status='pending')),
        rejected=Count('id', filter=Q(status='rejected')),
        total_downloads=Sum('download_count'),
        total_views=Sum('view_count'),
    )

    # Online users
    threshold = timezone.now() - timedelta(minutes=5)
    online_count = UserActivity.objects.filter(last_seen__gte=threshold).count()

    data = {
        'total_resources': resource_agg['total'],
        'total_users': User.objects.filter(is_active=True).count(),
        'pending_resources': resource_agg['pending'],
        'approved_resources': resource_agg['approved'],
        'rejected_resources': resource_agg['rejected'],
        'total_downloads': resource_agg['total_downloads'] or 0,
        'total_views': resource_agg['total_views'] or 0,
        'total_comments': Comment.objects.count(),
        'online_count': online_count,
    }
    cache.set(cache_key, data, 10)
    return JsonResponse(data)


# ============================================================
# HELPER
# ============================================================

def _time_ago(dt):
    """Chuyển datetime thành chuỗi 'x phút trước', 'x giờ trước'..."""
    now = timezone.now()
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return 'Vừa xong'
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f'{minutes} phút trước'
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f'{hours} giờ trước'
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f'{days} ngày trước'
    else:
        return dt.strftime('%d/%m/%Y')
