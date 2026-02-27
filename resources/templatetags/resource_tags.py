"""Template filters cho ứng dụng Resources."""

from django import template

register = template.Library()


@register.filter
def rating_display(value):
    """Hiển thị rating dưới dạng số thập phân 1 chữ số."""
    if value is None:
        return 0
    return round(float(value), 1)
