"""
Views cho Bảng điều khiển và Báo cáo thống kê.
Hiển thị tổng quan hệ thống và biểu đồ thống kê.
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDay
from django.http import JsonResponse
from django.utils import timezone
from resources.models import Resource, Comment, SubmissionLog
from categories.models import Category
from accounts.models import User
from accounts.decorators import admin_required


@admin_required
def dashboard(request):
    """
    Bảng điều khiển tổng quan - chỉ Admin.
    Hiển thị thống kê nhanh, hoạt động gần đây, tài liệu chờ duyệt.
    """
    # Thống kê tổng quan
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_resources': Resource.objects.count(),
        'approved_resources': Resource.objects.filter(status='approved').count(),
        'pending_resources': Resource.objects.filter(status='pending').count(),
        'rejected_resources': Resource.objects.filter(status='rejected').count(),
        'total_categories': Category.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_downloads': Resource.objects.aggregate(
            total=Sum('download_count')
        )['total'] or 0,
        'total_views': Resource.objects.aggregate(
            total=Sum('view_count')
        )['total'] or 0,
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

    context = {
        'stats': stats,
        'pending_resources': pending_resources,
        'recent_logs': recent_logs,
        'recent_users': recent_users,
        'top_resources': top_resources,
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
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_data = Resource.objects.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    chart_monthly = {
        'labels': [item['month'].strftime('%m/%Y') for item in monthly_data],
        'data': [item['count'] for item in monthly_data],
    }

    # 4. Top người đóng góp (biểu đồ cột ngang)
    top_contributors = User.objects.annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).filter(resource_count__gt=0).order_by('-resource_count')[:10]

    chart_contributors = {
        'labels': [user.full_name or user.username for user in top_contributors],
        'data': [user.resource_count for user in top_contributors],
    }

    # 5. Thống kê tổng hợp
    summary = {
        'total_resources': Resource.objects.count(),
        'approved': Resource.objects.filter(status='approved').count(),
        'pending': Resource.objects.filter(status='pending').count(),
        'rejected': Resource.objects.filter(status='rejected').count(),
        'total_views': Resource.objects.aggregate(total=Sum('view_count'))['total'] or 0,
        'total_downloads': Resource.objects.aggregate(total=Sum('download_count'))['total'] or 0,
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
