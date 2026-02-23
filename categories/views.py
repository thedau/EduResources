"""
Views cho ứng dụng Danh mục.
CRUD danh mục - chỉ Admin có quyền tạo, sửa, xóa.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Category
from .forms import CategoryForm
from accounts.decorators import admin_required


def category_list(request):
    """Hiển thị danh sách danh mục với số lượng tài liệu."""
    search_query = request.GET.get('q', '')

    categories = Category.objects.annotate(
        resource_count=Count('resources', filter=Q(resources__status='approved'))
    ).order_by('name')

    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Phân trang
    paginator = Paginator(categories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'categories/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


@admin_required
def category_create(request):
    """Tạo danh mục mới - chỉ Admin."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được tạo thành công.')
            return redirect('categories:list')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = CategoryForm()

    return render(request, 'categories/form.html', {
        'form': form,
        'title': 'Tạo danh mục mới',
        'is_edit': False,
    })


@admin_required
def category_edit(request, pk):
    """Chỉnh sửa danh mục - chỉ Admin."""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được cập nhật thành công.')
            return redirect('categories:list')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'categories/form.html', {
        'form': form,
        'category': category,
        'title': f'Chỉnh sửa: {category.name}',
        'is_edit': True,
    })


@admin_required
def category_delete(request, pk):
    """Xóa danh mục - chỉ Admin."""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = category.name
        resource_count = category.resources.count()
        if resource_count > 0:
            messages.error(
                request,
                f'Không thể xóa danh mục "{name}" vì còn {resource_count} tài liệu liên quan.'
            )
        else:
            category.delete()
            messages.success(request, f'Đã xóa danh mục "{name}" thành công.')

    return redirect('categories:list')
