"""
Views cho ứng dụng Tài liệu.
Xử lý: CRUD tài liệu, tìm kiếm, lọc, sắp xếp, bình luận,
quy trình duyệt (phê duyệt/từ chối), tải xuống tệp.
"""

import mimetypes
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q, Avg, Count, F
from django.http import FileResponse, Http404, JsonResponse
from .models import Resource, Comment, SubmissionLog
from .forms import ResourceForm, CommentForm, ResourceRejectForm
from categories.models import Category
from accounts.decorators import admin_required


def _invalidate_pending_cache():
    """Xóa cache pending_count khi trạng thái tài liệu thay đổi."""
    cache.delete('pending_resources_count')


def _annotate_resources(queryset):
    """Annotate queryset với average_rating và comment_count để tránh N+1 queries."""
    return queryset.annotate(
        avg_rating=Avg('comments__rating'),
        num_comments=Count('comments'),
    )


def resource_list(request):
    """
    Hiển thị danh sách tài liệu đã duyệt.
    Hỗ trợ tìm kiếm, lọc theo danh mục/loại, sắp xếp, phân trang.
    """
    # Lấy tham số từ query string
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    resource_type = request.GET.get('type', '')
    sort_by = request.GET.get('sort', '-created_at')

    # Chỉ hiển thị tài liệu đã duyệt, annotate để tránh N+1
    resources = _annotate_resources(
        Resource.objects.filter(
            status='approved'
        ).select_related('category', 'author')
    )

    # Tìm kiếm theo tiêu đề và mô tả
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Lọc theo danh mục
    if category_id:
        resources = resources.filter(category_id=category_id)

    # Lọc theo loại tài liệu
    if resource_type:
        resources = resources.filter(resource_type=resource_type)

    # Sắp xếp
    valid_sorts = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        '-view_count': '-view_count',
        'title': 'title',
        '-title': '-title',
        '-download_count': '-download_count',
    }
    sort_field = valid_sorts.get(sort_by, '-created_at')
    resources = resources.order_by(sort_field)

    # Phân trang
    paginator = Paginator(resources, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Danh sách danh mục và loại tài liệu cho bộ lọc
    categories = Category.objects.filter(is_active=True).order_by('name')

    return render(request, 'resources/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'resource_types': Resource.ResourceType.choices,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_type': resource_type,
        'selected_sort': sort_by,
    })


def resource_detail(request, slug):
    """
    Hiển thị chi tiết tài liệu kèm bình luận.
    Tăng lượt xem mỗi lần truy cập (dùng F() để tránh race condition).
    """
    resource = get_object_or_404(
        Resource.objects.select_related('category', 'author'),
        slug=slug,
    )

    # Chỉ cho xem tài liệu đã duyệt, hoặc chủ sở hữu/admin
    if resource.status != 'approved':
        if not request.user.is_authenticated:
            raise Http404
        if not (request.user == resource.author or request.user.is_admin):
            raise Http404

    # Tăng lượt xem (atomic, tránh race condition)
    # Sử dụng session để tránh đếm lại khi refresh trang
    viewed_key = f'viewed_resource_{resource.pk}'
    if not request.session.get(viewed_key, False):
        Resource.objects.filter(pk=resource.pk).update(view_count=F('view_count') + 1)
        resource.view_count += 1
        request.session[viewed_key] = True

    # Lấy bình luận
    comments = resource.comments.select_related('user').order_by('-created_at')
    comment_form = CommentForm()

    # Tài liệu liên quan (cùng danh mục), annotate rating
    related_resources = _annotate_resources(
        Resource.objects.filter(
            category=resource.category,
            status='approved'
        ).exclude(pk=resource.pk).select_related('category')
    ).order_by('-created_at')[:4]

    # Nhật ký duyệt (cho admin và tác giả)
    submission_logs = []
    if request.user.is_authenticated and (request.user == resource.author or request.user.is_admin):
        submission_logs = resource.submission_logs.select_related('reviewer').order_by('-created_at')

    return render(request, 'resources/detail.html', {
        'resource': resource,
        'comments': comments,
        'comment_form': comment_form,
        'related_resources': related_resources,
        'submission_logs': submission_logs,
    })


@login_required
def resource_create(request):
    """Tạo tài liệu mới - trạng thái mặc định: Chờ duyệt."""
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.author = request.user
            resource.status = Resource.Status.PENDING
            resource.save()

            # Ghi nhật ký
            SubmissionLog.objects.create(
                resource=resource,
                reviewer=request.user,
                old_status='',
                new_status=Resource.Status.PENDING,
                note='Tài liệu mới được gửi'
            )

            _invalidate_pending_cache()
            messages.success(request, 'Tài liệu đã được gửi và đang chờ duyệt.')
            return redirect('resources:my_resources')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = ResourceForm()

    return render(request, 'resources/form.html', {
        'form': form,
        'title': 'Tạo tài liệu mới',
        'is_edit': False,
    })


@login_required
def resource_edit(request, slug):
    """Chỉnh sửa tài liệu - chỉ chủ sở hữu hoặc Admin."""
    resource = get_object_or_404(Resource, slug=slug)

    # Kiểm tra quyền: chỉ tác giả hoặc admin
    if resource.author != request.user and not request.user.is_admin:
        messages.error(request, 'Bạn không có quyền chỉnh sửa tài liệu này.')
        return redirect('resources:detail', slug=slug)

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            updated_resource = form.save(commit=False)
            # Nếu người dùng thường chỉnh sửa, đặt lại trạng thái chờ duyệt
            if not request.user.is_admin and resource.status == 'approved':
                old_status = updated_resource.status
                updated_resource.status = Resource.Status.PENDING
                SubmissionLog.objects.create(
                    resource=updated_resource,
                    reviewer=request.user,
                    old_status=old_status,
                    new_status=Resource.Status.PENDING,
                    note='Tài liệu được chỉnh sửa, gửi lại để duyệt'
                )
            updated_resource.save()
            messages.success(request, 'Tài liệu đã được cập nhật thành công.')
            return redirect('resources:detail', slug=updated_resource.slug)
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = ResourceForm(instance=resource)

    return render(request, 'resources/form.html', {
        'form': form,
        'resource': resource,
        'title': f'Chỉnh sửa: {resource.title}',
        'is_edit': True,
    })


@login_required
def resource_delete(request, slug):
    """Xóa tài liệu - chỉ chủ sở hữu hoặc Admin."""
    resource = get_object_or_404(Resource, slug=slug)

    # Kiểm tra quyền
    if resource.author != request.user and not request.user.is_admin:
        messages.error(request, 'Bạn không có quyền xóa tài liệu này.')
        return redirect('resources:detail', slug=slug)

    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f'Đã xóa tài liệu "{title}" thành công.')
        return redirect('resources:my_resources')

    return redirect('resources:detail', slug=slug)


@login_required
def my_resources(request):
    """Hiển thị danh sách tài liệu của người dùng hiện tại."""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')

    resources = Resource.objects.filter(
        author=request.user
    ).select_related('category')

    if status_filter:
        resources = resources.filter(status=status_filter)

    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    resources = resources.order_by('-created_at')

    # Phân trang
    paginator = Paginator(resources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Thống kê - 1 query thay vì 4
    status_counts = dict(
        request.user.resources.values_list('status').annotate(c=Count('id')).values_list('status', 'c')
    )
    total = sum(status_counts.values())
    stats = {
        'total': total,
        'pending': status_counts.get('pending', 0),
        'approved': status_counts.get('approved', 0),
        'rejected': status_counts.get('rejected', 0),
    }

    return render(request, 'resources/my_resources.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'stats': stats,
        'statuses': Resource.Status.choices,
    })


@admin_required
def pending_resources(request):
    """Danh sách tài liệu chờ duyệt - chỉ Admin."""
    search_query = request.GET.get('q', '')

    resources = Resource.objects.filter(
        status='pending'
    ).select_related('category', 'author').order_by('created_at')

    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(author__full_name__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )

    # Phân trang
    paginator = Paginator(resources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'resources/pending_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'pending_count': Resource.objects.filter(status='pending').count(),
    })


@admin_required
def approve_resource(request, pk):
    """Phê duyệt tài liệu - chỉ Admin."""
    resource = get_object_or_404(Resource, pk=pk)

    if request.method == 'POST':
        old_status = resource.status
        resource.status = Resource.Status.APPROVED
        resource.rejection_reason = ''
        resource.save(update_fields=['status', 'rejection_reason'])

        # Ghi nhật ký
        SubmissionLog.objects.create(
            resource=resource,
            reviewer=request.user,
            old_status=old_status,
            new_status=Resource.Status.APPROVED,
            note='Tài liệu đã được phê duyệt'
        )

        messages.success(request, f'Đã phê duyệt tài liệu "{resource.title}".')
        _invalidate_pending_cache()

    return redirect('resources:pending')


@admin_required
def reject_resource(request, pk):
    """Từ chối tài liệu - chỉ Admin."""
    resource = get_object_or_404(Resource, pk=pk)

    if request.method == 'POST':
        form = ResourceRejectForm(request.POST)
        if form.is_valid():
            old_status = resource.status
            resource.status = Resource.Status.REJECTED
            resource.rejection_reason = form.cleaned_data['rejection_reason']
            resource.save(update_fields=['status', 'rejection_reason'])

            # Ghi nhật ký
            SubmissionLog.objects.create(
                resource=resource,
                reviewer=request.user,
                old_status=old_status,
                new_status=Resource.Status.REJECTED,
                note=form.cleaned_data['rejection_reason']
            )

            messages.success(request, f'Đã từ chối tài liệu "{resource.title}".')
            _invalidate_pending_cache()
        else:
            messages.error(request, 'Vui lòng nhập lý do từ chối.')

    return redirect('resources:pending')


@login_required
def download_resource(request, slug):
    """Tải xuống tệp đính kèm của tài liệu - yêu cầu đăng nhập."""
    resource = get_object_or_404(Resource, slug=slug, status='approved')

    if not resource.file:
        raise Http404('Tài liệu này không có tệp đính kèm.')

    # Tăng lượt tải (atomic)
    Resource.objects.filter(pk=resource.pk).update(download_count=F('download_count') + 1)

    # Trả về tệp
    content_type, _ = mimetypes.guess_type(resource.file.name)
    response = FileResponse(resource.file.open('rb'), content_type=content_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{resource.file.name.split("/")[-1]}"'
    return response


@login_required
def add_comment(request, slug):
    """Thêm bình luận cho tài liệu."""
    resource = get_object_or_404(Resource, slug=slug, status='approved')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.resource = resource
            comment.user = request.user
            comment.save()
            messages.success(request, 'Bình luận đã được thêm thành công.')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại nội dung bình luận.')

    return redirect('resources:detail', slug=slug)


@login_required
def delete_comment(request, pk):
    """Xóa bình luận - chỉ chủ sở hữu hoặc Admin."""
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user and not request.user.is_admin:
        messages.error(request, 'Bạn không có quyền xóa bình luận này.')
    elif request.method == 'POST':
        slug = comment.resource.slug
        comment.delete()
        messages.success(request, 'Bình luận đã được xóa.')
        return redirect('resources:detail', slug=slug)

    return redirect('resources:detail', slug=comment.resource.slug)


def preview_resource(request, slug):
    """
    Xem trước tài liệu PDF/Word ngay trên trình duyệt.
    - PDF: trả về trang preview dùng PDF.js để render
    - DOCX: chuyển đổi sang HTML bằng mammoth và trả về nội dung
    - DOC: không hỗ trợ preview trực tiếp
    """
    resource = get_object_or_404(Resource, slug=slug, status='approved')

    if not resource.file:
        raise Http404('Tài liệu này không có tệp đính kèm.')

    ext = resource.file_extension
    preview_type = None
    docx_html = None

    if ext == '.pdf':
        preview_type = 'pdf'
    elif ext == '.docx':
        preview_type = 'docx'
        try:
            import mammoth
            with resource.file.open('rb') as f:
                result = mammoth.convert_to_html(f)
                docx_html = result.value
        except Exception:
            docx_html = '<p class="text-danger">Không thể đọc nội dung tài liệu Word.</p>'
    elif ext == '.doc':
        preview_type = 'doc_unsupported'
    else:
        preview_type = 'unsupported'

    return render(request, 'resources/preview.html', {
        'resource': resource,
        'preview_type': preview_type,
        'docx_html': docx_html,
    })


def serve_file_inline(request, slug):
    """Phục vụ tệp PDF inline (không download) để PDF.js có thể đọc."""
    resource = get_object_or_404(Resource, slug=slug, status='approved')

    if not resource.file or resource.file_extension != '.pdf':
        raise Http404

    content_type = 'application/pdf'
    response = FileResponse(resource.file.open('rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(resource.file.name)}"'
    return response
