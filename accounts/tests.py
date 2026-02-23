"""
Tests cho ứng dụng accounts.
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class UserModelTest(TestCase):
    """Test model User."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            full_name='Test Admin',
            email='admin@test.com',
            role=User.Role.ADMIN,
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            email='user@test.com',
            role=User.Role.USER,
        )
        self.guest = User.objects.create_user(
            username='testguest',
            password='testpass123',
            full_name='Test Guest',
            email='guest@test.com',
            role=User.Role.GUEST,
        )

    def test_user_creation(self):
        """Kiểm tra tạo người dùng."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.full_name, 'Test User')
        self.assertEqual(self.user.role, User.Role.USER)

    def test_user_str(self):
        """Kiểm tra __str__."""
        self.assertEqual(str(self.user), 'Test User')
        guest_no_name = User.objects.create_user(
            username='noname', password='test123'
        )
        self.assertEqual(str(guest_no_name), 'noname')

    def test_is_admin_property(self):
        """Kiểm tra property is_admin."""
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.guest.is_admin)

    def test_is_user_property(self):
        """Kiểm tra property is_user."""
        self.assertFalse(self.admin.is_user)
        self.assertTrue(self.user.is_user)
        self.assertFalse(self.guest.is_user)

    def test_is_guest_property(self):
        """Kiểm tra property is_guest."""
        self.assertFalse(self.admin.is_guest)
        self.assertFalse(self.user.is_guest)
        self.assertTrue(self.guest.is_guest)

    def test_display_role(self):
        """Kiểm tra hiển thị vai trò."""
        self.assertEqual(self.admin.display_role, 'Quản trị viên')
        self.assertEqual(self.user.display_role, 'Người dùng')
        self.assertEqual(self.guest.display_role, 'Khách')

    def test_default_role(self):
        """Kiểm tra vai trò mặc định là user."""
        new_user = User.objects.create_user(
            username='newuser', password='testpass123'
        )
        self.assertEqual(new_user.role, User.Role.USER)


class AuthViewsTest(TestCase):
    """Test views xác thực."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            email='user@test.com',
            role=User.Role.USER,
        )

    def test_login_page(self):
        """Kiểm tra trang đăng nhập."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Đăng nhập')

    def test_register_page(self):
        """Kiểm tra trang đăng ký."""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Đăng ký')

    def test_login_success(self):
        """Kiểm tra đăng nhập thành công."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        """Kiểm tra đăng nhập sai mật khẩu."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        """Kiểm tra đăng ký thành công."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'password1': 'Str0ngP@ss!',
            'password2': 'Str0ngP@ss!',
            'full_name': 'New User',
            'email': 'new@test.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_logout(self):
        """Kiểm tra đăng xuất."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        """Kiểm tra trang profile cần đăng nhập."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_authenticated(self):
        """Kiểm tra trang profile khi đã đăng nhập."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_manage_users_requires_admin(self):
        """Kiểm tra quản lý người dùng cần quyền admin."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:manage_users'))
        self.assertEqual(response.status_code, 302)
