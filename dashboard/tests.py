"""
Tests cho ứng dụng dashboard.
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class DashboardViewsTest(TestCase):
    """Test views dashboard."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role=User.Role.ADMIN,
        )
        self.user = User.objects.create_user(
            username='user',
            password='user123',
            role=User.Role.USER,
        )

    def test_dashboard_requires_admin(self):
        """Kiểm tra dashboard cần quyền admin."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_admin_access(self):
        """Kiểm tra admin truy cập dashboard."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)

    def test_reports_requires_admin(self):
        """Kiểm tra báo cáo cần quyền admin."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('dashboard:reports'))
        self.assertEqual(response.status_code, 302)

    def test_reports_admin_access(self):
        """Kiểm tra admin truy cập báo cáo."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('dashboard:reports'))
        self.assertEqual(response.status_code, 200)
