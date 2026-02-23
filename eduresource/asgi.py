"""
Cấu hình ASGI cho dự án EduResource.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduresource.settings')
application = get_asgi_application()
