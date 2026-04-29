"""
Views cho tính năng AI.
Bao gồm: tóm tắt tài liệu, chatbot trợ giảng, gợi ý tag.
"""

import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from resources.models import Resource
from .services import summarize_resource, chat_about_resource, suggest_tags, general_chat, _extract_file_content


@login_required
@ratelimit(key='user', rate='20/h', method='POST', block=True)
@require_POST
def api_summarize(request, slug):
    """API tóm tắt tài liệu bằng AI."""
    resource = get_object_or_404(Resource, slug=slug)

    # Kiểm tra quyền: chỉ xem được tài liệu đã duyệt hoặc tài liệu của mình
    if resource.status != 'approved' and resource.author != request.user and not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Không có quyền truy cập.'}, status=403)

    # Kiểm tra cache trong session
    cache_key = f'ai_summary_{resource.pk}'
    cached = request.session.get(cache_key)
    if cached:
        return JsonResponse({'success': True, 'summary': cached, 'cached': True})

    success, summary = summarize_resource(resource)

    if success:
        # Cache trong session (giảm API calls)
        request.session[cache_key] = summary
        return JsonResponse({'success': True, 'summary': summary})
    else:
        return JsonResponse({'success': False, 'error': summary}, status=400)


@login_required
@ratelimit(key='user', rate='60/h', method='POST', block=True)
@require_POST
def api_chat(request, slug):
    """API chatbot hỏi đáp về tài liệu."""
    resource = get_object_or_404(Resource, slug=slug)

    # Kiểm tra quyền
    if resource.status != 'approved' and resource.author != request.user and not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Không có quyền truy cập.'}, status=403)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ.'}, status=400)

    message = body.get('message', '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Vui lòng nhập câu hỏi.'}, status=400)

    if len(message) > 1000:
        return JsonResponse({'success': False, 'error': 'Câu hỏi quá dài (tối đa 1000 ký tự).'}, status=400)

    # Lấy lịch sử chat từ request
    chat_history = body.get('history', [])

    success, reply = chat_about_resource(resource, message, chat_history)

    if success:
        return JsonResponse({'success': True, 'reply': reply})
    else:
        return JsonResponse({'success': False, 'error': reply}, status=400)


@login_required
@ratelimit(key='user', rate='30/h', method='POST', block=True)
@require_POST
def api_suggest_tags(request):
    """API gợi ý danh mục và tag cho tài liệu."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ.'}, status=400)

    title = body.get('title', '').strip()
    description = body.get('description', '').strip()
    content = body.get('content', '').strip()

    if not title:
        return JsonResponse({'success': False, 'error': 'Cần ít nhất tiêu đề.'}, status=400)

    # Nếu đang edit resource có file, trích xuất nội dung
    file_content = ""
    resource_id = body.get('resource_id')
    if resource_id:
        try:
            resource = Resource.objects.get(pk=resource_id)
            if resource.status != 'approved' and resource.author != request.user and not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'Không có quyền truy cập.'}, status=403)
            file_content = _extract_file_content(resource)
        except Resource.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Tài liệu không tồn tại.'}, status=404)

    success, suggestions = suggest_tags(title, description, content, file_content)

    if success:
        return JsonResponse({'success': True, 'suggestions': suggestions})
    else:
        return JsonResponse({'success': False, 'error': suggestions.get('error', 'Lỗi AI')}, status=400)


@login_required
@ratelimit(key='user', rate='60/h', method='POST', block=True)
@require_POST
def api_general_chat(request):
    """API chatbot tổng quát cho website."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ.'}, status=400)

    message = body.get('message', '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Vui lòng nhập câu hỏi.'}, status=400)

    if len(message) > 1000:
        return JsonResponse({'success': False, 'error': 'Câu hỏi quá dài (tối đa 1000 ký tự).'}, status=400)

    chat_history = body.get('history', [])

    success, reply = general_chat(message, chat_history)

    if success:
        return JsonResponse({'success': True, 'reply': reply})
    else:
        return JsonResponse({'success': False, 'error': reply}, status=400)
