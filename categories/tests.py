"""
Tests cho ứng dụng categories.
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from categories.models import Category


class CategoryModelTest(TestCase):
    """Test model Category."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Toán học',
            description='Danh mục tài liệu Toán học',
            icon='fas fa-calculator',
        )

    def test_category_creation(self):
        """Kiểm tra tạo danh mục."""
        self.assertEqual(self.category.name, 'Toán học')
        self.assertTrue(self.category.is_active)

    def test_category_str(self):
        """Kiểm tra __str__."""
        self.assertEqual(str(self.category), 'Toán học')

    def test_slug_auto_generation(self):
        """Kiểm tra tự động tạo slug."""
        self.assertTrue(len(self.category.slug) > 0)

    def test_slug_unique(self):
        """Kiểm tra slug duy nhất."""
        cat2 = Category.objects.create(name='Toán học nâng cao')
        self.assertNotEqual(self.category.slug, cat2.slug)

    def test_parent_category(self):
        """Kiểm tra danh mục cha."""
        child = Category.objects.create(
            name='Đại số',
            parent=self.category,
        )
        self.assertEqual(child.parent, self.category)
        self.assertIn(child, self.category.children.all())


class CategoryViewsTest(TestCase):
    """Test views danh mục."""

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
        self.category = Category.objects.create(
            name='Tin học',
            description='Tài liệu Tin học',
        )

    def test_category_list(self):
        """Kiểm tra danh sách danh mục."""
        response = self.client.get(reverse('categories:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tin học')

    def test_category_create_requires_admin(self):
        """Kiểm tra tạo danh mục cần quyền admin."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('categories:create'))
        self.assertEqual(response.status_code, 302)

    def test_category_create_admin(self):
        """Kiểm tra admin tạo danh mục."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('categories:create'))
        self.assertEqual(response.status_code, 200)

    def test_category_create_post(self):
        """Kiểm tra tạo danh mục bằng POST."""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('categories:create'), {
            'name': 'Vật lý',
            'description': 'Tài liệu Vật lý',
            'icon': 'fas fa-atom',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Vật lý').exists())

    def test_category_edit(self):
        """Kiểm tra chỉnh sửa danh mục."""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            reverse('categories:edit', args=[self.category.pk]),
            {
                'name': 'Công nghệ thông tin',
                'description': 'Tài liệu CNTT',
                'icon': 'fas fa-laptop',
                'is_active': True,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Công nghệ thông tin')

    def test_category_delete(self):
        """Kiểm tra xóa danh mục."""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            reverse('categories:delete', args=[self.category.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(name='Tin học').exists())
