"""
Dịch vụ AI sử dụng Groq API (LLaMA 3).
Cung cấp: tóm tắt tài liệu, chatbot trợ giảng, gợi ý danh mục/tag.
"""

import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy singleton cho Groq client
_client = None

GROQ_MODEL = 'llama-3.3-70b-versatile'


def _get_client():
    """Khởi tạo Groq client (lazy singleton)."""
    global _client
    if _client is None:
        try:
            from groq import Groq

            api_key = getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
            if not api_key:
                logger.warning("GROQ_API_KEY chưa được cấu hình.")
                return None

            _client = Groq(api_key=api_key)
        except ImportError:
            logger.error("Chưa cài đặt groq. Chạy: pip install groq")
            return None
        except Exception as e:
            logger.error(f"Lỗi khởi tạo Groq: {e}")
            return None
    return _client


def _chat_completion(messages, max_tokens=2048, temperature=0.7):
    """Gọi Groq chat completion API."""
    client = _get_client()
    if not client:
        return None

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def _extract_file_content(resource):
    """
    Trích xuất nội dung văn bản từ file đính kèm.
    Hỗ trợ: PDF, DOCX, TXT.
    """
    if not resource.file:
        return ""

    ext = resource.file_extension
    content = ""

    try:
        if ext == '.pdf':
            try:
                import PyPDF2
                with resource.file.open('rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    pages = []
                    for page in reader.pages[:20]:  # Giới hạn 20 trang
                        text = page.extract_text()
                        if text:
                            pages.append(text)
                    content = "\n".join(pages)
            except ImportError:
                pass

        elif ext == '.docx':
            try:
                import mammoth
                with resource.file.open('rb') as f:
                    result = mammoth.extract_raw_text(f)
                    content = result.value
            except ImportError:
                pass

        elif ext in ('.txt', '.md'):
            with resource.file.open('r') as f:
                content = f.read()

    except Exception as e:
        logger.error(f"Lỗi trích xuất nội dung file: {e}")

    # Giới hạn 15000 ký tự để tránh vượt token limit
    return content[:15000] if content else ""


def _build_resource_context(resource):
    """Tạo ngữ cảnh đầy đủ của tài liệu cho AI. Ưu tiên nội dung file đính kèm."""
    parts = [
        f"Tiêu đề: {resource.title}",
        f"Loại: {resource.get_resource_type_display()}",
        f"Danh mục: {resource.category.name}",
    ]

    # Ưu tiên nội dung file đính kèm (PDF, DOCX, TXT)
    file_content = _extract_file_content(resource)
    if file_content:
        parts.append(f"Nội dung tài liệu:\n{file_content}")
    else:
        # Chỉ dùng nội dung nhập tay nếu không có file
        if resource.content:
            parts.append(f"Nội dung tài liệu:\n{resource.content[:8000]}")
        elif resource.description:
            parts.append(f"Mô tả tài liệu: {resource.description}")

    return "\n\n".join(parts)


def summarize_resource(resource):
    """
    Tóm tắt nội dung tài liệu bằng AI.
    Returns: (success: bool, summary: str)
    """
    client = _get_client()
    if not client:
        return False, "Chưa cấu hình API key. Vui lòng thêm GROQ_API_KEY vào file .env"

    context = _build_resource_context(resource)
    if not context or len(context.strip()) < 50:
        return False, "Tài liệu không có đủ nội dung để tóm tắt."

    prompt = f"""Bạn là trợ lý giáo dục chuyên tóm tắt tài liệu học tập bằng tiếng Việt.

Hãy tóm tắt tài liệu sau một cách ngắn gọn, rõ ràng, bao gồm:
1. **Chủ đề chính**: Tài liệu nói về gì?
2. **Các ý chính**: Liệt kê 3-5 ý chính quan trọng nhất
3. **Đối tượng phù hợp**: Tài liệu phù hợp với ai?
4. **Từ khóa**: 5-8 từ khóa chính

Tài liệu cần tóm tắt:
---
{context}
---

Trả lời bằng tiếng Việt, định dạng dễ đọc."""

    try:
        messages = [
            {"role": "system", "content": "Bạn là trợ lý giáo dục chuyên tóm tắt tài liệu học tập bằng tiếng Việt."},
            {"role": "user", "content": prompt},
        ]
        result = _chat_completion(messages, max_tokens=2048, temperature=0.5)
        if result:
            return True, result
        return False, "AI không thể tạo tóm tắt. Vui lòng thử lại."
    except Exception as e:
        logger.error(f"Lỗi Groq summarize: {e}")
        return False, f"Lỗi khi gọi AI: {str(e)}"


def chat_about_resource(resource, user_message, chat_history=None):
    """
    Chat hỏi đáp về tài liệu.
    Args:
        resource: Resource object
        user_message: Câu hỏi của người dùng
        chat_history: list of dicts [{'role': 'user'/'assistant', 'content': '...'}]
    Returns: (success: bool, reply: str)
    """
    client = _get_client()
    if not client:
        return False, "Chưa cấu hình API key. Vui lòng thêm GROQ_API_KEY vào file .env"

    context = _build_resource_context(resource)

    system_prompt = f"""Bạn là trợ giảng AI thông minh cho nền tảng học tập EduResource.
Bạn đang trả lời câu hỏi về tài liệu sau:

---
{context}
---

Quy tắc:
- Trả lời bằng tiếng Việt, thân thiện và dễ hiểu
- Chỉ trả lời dựa trên nội dung tài liệu được cung cấp
- Nếu câu hỏi ngoài phạm vi tài liệu, hãy nói rõ và gợi ý tìm kiếm thêm
- Giải thích dễ hiểu, sử dụng ví dụ khi cần
- Trả lời ngắn gọn nhưng đầy đủ (tối đa 500 từ)
- Có thể sử dụng markdown để định dạng"""

    # Xây dựng messages cho Groq
    messages = [{"role": "system", "content": system_prompt}]

    # Thêm lịch sử chat (giới hạn 10 tin nhắn gần nhất)
    if chat_history:
        for msg in chat_history[-10:]:
            role = 'user' if msg['role'] == 'user' else 'assistant'
            messages.append({"role": role, "content": msg['content']})

    # Thêm tin nhắn hiện tại
    messages.append({"role": "user", "content": user_message})

    try:
        result = _chat_completion(messages, max_tokens=1024, temperature=0.7)
        if result:
            return True, result
        return False, "AI không thể phản hồi. Vui lòng thử lại."
    except Exception as e:
        logger.error(f"Lỗi Groq chat: {e}")
        return False, f"Lỗi khi gọi AI: {str(e)}"


def suggest_tags(title, description="", content="", file_content=""):
    """
    Gợi ý danh mục và tag cho tài liệu dựa trên nội dung.
    Returns: (success: bool, suggestions: dict)
    """
    client = _get_client()
    if not client:
        return False, {"error": "Chưa cấu hình API key."}

    # Lấy danh sách danh mục hiện có
    from categories.models import Category
    categories = list(
        Category.objects.filter(is_active=True).values_list('name', flat=True)
    )

    text_parts = []
    if title:
        text_parts.append(f"Tiêu đề: {title}")
    if description:
        text_parts.append(f"Mô tả: {description}")
    if content:
        text_parts.append(f"Nội dung: {content[:3000]}")
    if file_content:
        text_parts.append(f"Nội dung file: {file_content[:5000]}")

    combined_text = "\n".join(text_parts)

    if len(combined_text.strip()) < 10:
        return False, {"error": "Cần ít nhất tiêu đề để gợi ý."}

    prompt = f"""Bạn là hệ thống phân loại tài liệu học tập thông minh.

Danh sách danh mục có sẵn: {', '.join(categories) if categories else 'Chưa có'}

Dựa trên thông tin tài liệu bên dưới, hãy gợi ý:
1. Danh mục phù hợp nhất (chọn từ danh sách có sẵn, nếu không phù hợp thì gợi ý danh mục mới)
2. Loại tài liệu phù hợp (document/video/presentation/exercise/other)
3. 5-8 từ khóa/tag liên quan

Thông tin tài liệu:
---
{combined_text}
---

Trả lời theo định dạng JSON (không có markdown code block):
{{"category": "Tên danh mục", "resource_type": "document", "tags": ["tag1", "tag2", "tag3"], "confidence": 0.85, "reason": "Lý do gợi ý ngắn gọn"}}"""

    try:
        messages = [
            {"role": "system", "content": "Bạn là hệ thống phân loại tài liệu. Luôn trả lời bằng JSON hợp lệ, không có markdown code block."},
            {"role": "user", "content": prompt},
        ]
        result = _chat_completion(messages, max_tokens=512, temperature=0.3)
        if result:
            import json
            # Làm sạch response
            text = result.strip()
            # Bỏ markdown code block nếu có
            if text.startswith('```'):
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                text = text.rsplit('```', 1)[0]
            text = text.strip()

            try:
                suggestions = json.loads(text)
                return True, suggestions
            except json.JSONDecodeError:
                return True, {
                    "category": "",
                    "resource_type": "document",
                    "tags": [],
                    "raw_response": result
                }
        return False, {"error": "AI không thể phân tích. Vui lòng thử lại."}
    except Exception as e:
        logger.error(f"Lỗi Groq suggest_tags: {e}")
        return False, {"error": f"Lỗi khi gọi AI: {str(e)}"}


def general_chat(user_message, chat_history=None):
    """
    Chatbot tổng quát cho website EduResource.
    Hỗ trợ người dùng tìm kiếm tài liệu, hướng dẫn sử dụng, trả lời câu hỏi chung.
    Args:
        user_message: Câu hỏi của người dùng
        chat_history: list of dicts [{'role': 'user'/'assistant', 'content': '...'}]
    Returns: (success: bool, reply: str)
    """
    client = _get_client()
    if not client:
        return False, "Chưa cấu hình API key. Vui lòng thêm GROQ_API_KEY vào file .env"

    # Lấy thống kê cơ bản để chatbot có context
    from resources.models import Resource
    from categories.models import Category

    total_resources = Resource.objects.filter(status='approved').count()
    categories_list = list(
        Category.objects.filter(is_active=True).values_list('name', flat=True)
    )
    recent_resources = list(
        Resource.objects.filter(status='approved')
        .order_by('-created_at')[:5]
        .values_list('title', flat=True)
    )

    system_prompt = f"""Bạn là EduBot - trợ lý AI thông minh của nền tảng học tập EduResource.

Thông tin về hệ thống:
- EduResource là thư viện tài liệu học tập trực tuyến
- Hiện có {total_resources} tài liệu đã được duyệt
- Các danh mục: {', '.join(categories_list) if categories_list else 'Chưa có'}
- Tài liệu mới nhất: {', '.join(recent_resources) if recent_resources else 'Chưa có'}

Chức năng chính của website:
- Tìm kiếm và xem tài liệu học tập
- Đăng tải và chia sẻ tài liệu
- Bình luận và đánh giá tài liệu
- AI tóm tắt nội dung tài liệu
- Quản lý danh mục tài liệu

Quy tắc:
- Luôn trả lời bằng tiếng Việt, thân thiện và nhiệt tình
- Giúp người dùng tìm tài liệu phù hợp
- Hướng dẫn cách sử dụng website
- Trả lời các câu hỏi về học tập và giáo dục
- Gợi ý tài liệu liên quan khi có thể
- Trả lời ngắn gọn, dễ hiểu (tối đa 300 từ)
- Sử dụng emoji phù hợp để thân thiện hơn
- Nếu không biết, hãy nói thật và gợi ý hướng khác"""

    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        for msg in chat_history[-10:]:
            role = 'user' if msg['role'] == 'user' else 'assistant'
            messages.append({"role": role, "content": msg['content']})

    messages.append({"role": "user", "content": user_message})

    try:
        result = _chat_completion(messages, max_tokens=1024, temperature=0.7)
        if result:
            return True, result
        return False, "Xin lỗi, mình không thể trả lời lúc này. Vui lòng thử lại!"
    except Exception as e:
        logger.error(f"Lỗi Groq general_chat: {e}")
        return False, f"Lỗi khi gọi AI: {str(e)}"
