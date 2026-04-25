"""
Views cho Bảng điều khiển và Báo cáo thống kê.
Hiển thị tổng quan hệ thống và biểu đồ thống kê.
"""

import json
from datetime import datetime
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from resources.models import Resource, Comment, SubmissionLog
from categories.models import Category
from accounts.models import User
from accounts.decorators import admin_required


def _build_monthly_chart_data(month_count=12, status=None):
    """Tạo dữ liệu biểu đồ theo tháng, không phụ thuộc hàm datetime của DB."""
    now = timezone.now()
    month_pairs = []
    for offset in range(month_count - 1, -1, -1):
        month = now.month - offset
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        month_pairs.append((year, month))

    monthly_map = {(year, month): 0 for year, month in month_pairs}

    resources = Resource.objects.filter(created_at__isnull=False)
    if status:
        resources = resources.filter(status=status)

    for created_at in resources.values_list('created_at', flat=True):
        if not created_at:
            continue
        key = (created_at.year, created_at.month)
        if key in monthly_map:
            monthly_map[key] += 1

    return {
        'labels': [datetime(year, month, 1).strftime('%m/%Y') for year, month in month_pairs],
        'data': [monthly_map[(year, month)] for year, month in month_pairs],
    }


@admin_required
def dashboard(request):
    """
    Bảng điều khiển tổng quan - chỉ Admin.
    Hiển thị thống kê nhanh, hoạt động gần đây, tài liệu chờ duyệt.
    """
    # Thống kê tổng quan - gộp thành ít query nhất
    resource_agg = Resource.objects.aggregate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='approved')),
        pending=Count('id', filter=Q(status='pending')),
        rejected=Count('id', filter=Q(status='rejected')),
        total_downloads=Sum('download_count'),
        total_views=Sum('view_count'),
    )

    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_resources': resource_agg['total'],
        'approved_resources': resource_agg['approved'],
        'pending_resources': resource_agg['pending'],
        'rejected_resources': resource_agg['rejected'],
        'total_categories': Category.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_downloads': resource_agg['total_downloads'] or 0,
        'total_views': resource_agg['total_views'] or 0,
    }

    # Tài liệu chờ duyệt gần đây
    pending_resources = Resource.objects.filter(
        status='pending'
    ).select_related('author', 'category').order_by('created_at')[:5]

    # Hoạt động gần đây (nhật ký duyệt)
    recent_logs = SubmissionLog.objects.select_related(
        'resource', 'reviewer'
    ).order_by('-created_at')[:10]

    # Người dùng mới đăng ký
    recent_users = User.objects.order_by('-date_joined')[:5]

    # Tài liệu phổ biến nhất
    top_resources = Resource.objects.filter(
        status='approved'
    ).order_by('-view_count')[:5]

    # Dữ liệu biểu đồ nhanh trên dashboard
    chart_status = {
        'labels': ['Đã duyệt', 'Chờ duyệt', 'Từ chối'],
        'data': [
            stats['approved_resources'],
            stats['pending_resources'],
            stats['rejected_resources'],
        ],
    }

    chart_monthly = _build_monthly_chart_data(month_count=6)

    category_data = Category.objects.annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).filter(resource_count__gt=0).order_by('-resource_count')[:6]

    chart_categories = {
        'labels': [cat.name for cat in category_data],
        'data': [cat.resource_count for cat in category_data],
    }

    context = {
        'stats': stats,
        'pending_resources': pending_resources,
        'recent_logs': recent_logs,
        'recent_users': recent_users,
        'top_resources': top_resources,
        'chart_status': json.dumps(chart_status, ensure_ascii=False),
        'chart_monthly': json.dumps(chart_monthly, ensure_ascii=False),
        'chart_categories': json.dumps(chart_categories, ensure_ascii=False),
    }
    return render(request, 'dashboard/index.html', context)


@admin_required
def reports(request):
    """
    Trang báo cáo thống kê với biểu đồ - chỉ Admin.
    Dữ liệu cho Chart.js được nhúng trực tiếp trong template.
    """
    # 1. Tài liệu theo danh mục (biểu đồ cột)
    categories_data = Category.objects.annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).filter(resource_count__gt=0).order_by('-resource_count')[:10]

    chart_categories = {
        'labels': [cat.name for cat in categories_data],
        'data': [cat.resource_count for cat in categories_data],
    }

    # 2. Tài liệu theo trạng thái (biểu đồ tròn)
    status_data = Resource.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    status_map = dict(Resource.Status.choices)
    chart_status = {
        'labels': [status_map.get(item['status'], item['status']) for item in status_data],
        'data': [item['count'] for item in status_data],
    }

    # 3. Tài liệu theo tháng (biểu đồ đường - 12 tháng gần nhất)
    chart_monthly = _build_monthly_chart_data(month_count=12)

    # 4. Top người đóng góp (biểu đồ cột ngang)
    top_contributors = User.objects.annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).filter(resource_count__gt=0).order_by('-resource_count')[:10]

    chart_contributors = {
        'labels': [user.full_name or user.username for user in top_contributors],
        'data': [user.resource_count for user in top_contributors],
    }

    if not chart_contributors['labels']:
        chart_contributors = {
            'labels': ['Chưa có dữ liệu'],
            'data': [0],
        }

    # 5. Thống kê tổng hợp - gộp 1 query
    summary_agg = Resource.objects.aggregate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='approved')),
        pending=Count('id', filter=Q(status='pending')),
        rejected=Count('id', filter=Q(status='rejected')),
        total_views=Sum('view_count'),
        total_downloads=Sum('download_count'),
    )

    summary = {
        'total_resources': summary_agg['total'],
        'approved': summary_agg['approved'],
        'pending': summary_agg['pending'],
        'rejected': summary_agg['rejected'],
        'total_views': summary_agg['total_views'] or 0,
        'total_downloads': summary_agg['total_downloads'] or 0,
        'total_comments': Comment.objects.count(),
        'total_users': User.objects.filter(is_active=True).count(),
    }

    context = {
        'chart_categories': json.dumps(chart_categories, ensure_ascii=False),
        'chart_status': json.dumps(chart_status, ensure_ascii=False),
        'chart_monthly': json.dumps(chart_monthly, ensure_ascii=False),
        'chart_contributors': json.dumps(chart_contributors, ensure_ascii=False),
        'summary': summary,
    }
    return render(request, 'dashboard/reports.html', context)
