"""
Dịch vụ AI sử dụng Google Gemini API.
Cung cấp: tóm tắt tài liệu, chatbot trợ giảng, gợi ý danh mục/tag.
"""

import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy import để tránh lỗi khi chưa cài đặt
_genai = None
_model = None


def _get_model():
    """Khởi tạo Gemini model (lazy singleton)."""
    global _genai, _model
    if _model is None:
        try:
            import google.generativeai as genai
            _genai = genai

            api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
            if not api_key:
                logger.warning("GEMINI_API_KEY chưa được cấu hình.")
                return None

            genai.configure(api_key=api_key)
            _model = genai.GenerativeModel('gemini-2.0-flash')
        except ImportError:
            logger.error("Chưa cài đặt google-generativeai. Chạy: pip install google-generativeai")
            return None
        except Exception as e:
            logger.error(f"Lỗi khởi tạo Gemini: {e}")
            return None
    return _model


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
    """Tạo ngữ cảnh đầy đủ của tài liệu cho AI."""
    parts = [
        f"Tiêu đề: {resource.title}",
        f"Loại: {resource.get_resource_type_display()}",
        f"Danh mục: {resource.category.name}",
    ]
    if resource.description:
        parts.append(f"Mô tả: {resource.description}")
    if resource.content:
        parts.append(f"Nội dung chi tiết:\n{resource.content[:5000]}")

    file_content = _extract_file_content(resource)
    if file_content:
        parts.append(f"Nội dung file đính kèm:\n{file_content}")

    return "\n\n".join(parts)


def summarize_resource(resource):
    """
    Tóm tắt nội dung tài liệu bằng AI.
    Returns: (success: bool, summary: str)
    """
    model = _get_model()
    if not model:
        return False, "Chưa cấu hình API key. Vui lòng thêm GEMINI_API_KEY vào file .env"

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
        response = model.generate_content(prompt)
        if response and response.text:
            return True, response.text
        return False, "AI không thể tạo tóm tắt. Vui lòng thử lại."
    except Exception as e:
        logger.error(f"Lỗi Gemini summarize: {e}")
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
    model = _get_model()
    if not model:
        return False, "Chưa cấu hình API key. Vui lòng thêm GEMINI_API_KEY vào file .env"

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

    # Xây dựng lịch sử chat cho Gemini
    contents = []

    # System prompt as first user turn
    contents.append({
        'role': 'user',
        'parts': [system_prompt + "\n\nHãy xác nhận bạn đã hiểu vai trò."]
    })
    contents.append({
        'role': 'model',
        'parts': ["Tôi đã hiểu. Tôi là trợ giảng AI của EduResource, sẵn sàng trả lời câu hỏi về tài liệu này. Bạn có thể hỏi tôi bất cứ điều gì!"]
    })

    # Thêm lịch sử chat (giới hạn 10 tin nhắn gần nhất)
    if chat_history:
        for msg in chat_history[-10:]:
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append({
                'role': role,
                'parts': [msg['content']]
            })

    # Thêm tin nhắn hiện tại
    contents.append({
        'role': 'user',
        'parts': [user_message]
    })

    try:
        response = model.generate_content(contents)
        if response and response.text:
            return True, response.text
        return False, "AI không thể phản hồi. Vui lòng thử lại."
    except Exception as e:
        logger.error(f"Lỗi Gemini chat: {e}")
        return False, f"Lỗi khi gọi AI: {str(e)}"


def suggest_tags(title, description="", content="", file_content=""):
    """
    Gợi ý danh mục và tag cho tài liệu dựa trên nội dung.
    Returns: (success: bool, suggestions: dict)
    """
    model = _get_model()
    if not model:
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
        response = model.generate_content(prompt)
        if response and response.text:
            import json
            # Làm sạch response
            text = response.text.strip()
            # Bỏ markdown code block nếu có
            if text.startswith('```'):
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                text = text.rsplit('```', 1)[0]
            text = text.strip()

            try:
                suggestions = json.loads(text)
                return True, suggestions
            except json.JSONDecodeError:
                # Nếu không parse được JSON, trả về text thô
                return True, {
                    "category": "",
                    "resource_type": "document",
                    "tags": [],
                    "raw_response": response.text
                }
        return False, {"error": "AI không thể phân tích. Vui lòng thử lại."}
    except Exception as e:
        logger.error(f"Lỗi Gemini suggest_tags: {e}")
        return False, {"error": f"Lỗi khi gọi AI: {str(e)}"}
