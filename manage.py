#!/usr/bin/env python
"""Django command-line utility - Quản lý dự án EduResource."""
import os
import sys


def main():
    """Chạy các tác vụ quản trị Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduresource.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Không thể import Django. Hãy đảm bảo Django đã được cài đặt "
            "và có sẵn trong PYTHONPATH. Bạn đã kích hoạt môi trường ảo chưa?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
