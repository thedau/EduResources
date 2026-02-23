"""
Tests cho ứng dụng resources.
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from categories.models import Category
from resources.models import Resource, Comment, SubmissionLog


class ResourceModelTest(TestCase):
    """Test model Resource."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='testpass123',
            full_name='Tác giả',
            role=User.Role.USER,
        )
        self.category = Category.objects.create(
            name='Toán học',
            description='Toán'
        )
        self.resource = Resource.objects.create(
            title='Giáo trình Giải tích',
            description='Mô tả giáo trình',
            content='Nội dung chi tiết giáo trình Giải tích',
            category=self.category,
            author=self.user,
            resource_type='document',
        )

    def test_resource_creation(self):
        """Kiểm tra tạo tài liệu."""
        self.assertEqual(self.resource.title, 'Giáo trình Giải tích')
        self.assertEqual(self.resource.author, self.user)
        self.assertEqual(self.resource.category, self.category)

    def test_default_status_pending(self):
        """Kiểm tra trạng thái mặc định là chờ duyệt."""
        self.assertEqual(self.resource.status, 'pending')

    def test_resource_str(self):
        """Kiểm tra __str__."""
        self.assertEqual(str(self.resource), 'Giáo trình Giải tích')

    def test_slug_auto_generation(self):
        """Kiểm tra tự động tạo slug."""
        self.assertTrue(len(self.resource.slug) > 0)

    def test_view_count_default(self):
        """Kiểm tra lượt xem mặc định."""
        self.assertEqual(self.resource.view_count, 0)


class CommentModelTest(TestCase):
    """Test model Comment."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='commenter', password='testpass123', role=User.Role.USER
        )
        self.category = Category.objects.create(name='Tin học')
        self.resource = Resource.objects.create(
            title='Python cơ bản',
            description='Mô tả',
            content='Nội dung',
            category=self.category,
            author=self.user,
        )
        self.comment = Comment.objects.create(
            resource=self.resource,
            user=self.user,
            content='Bình luận test',
            rating=5,
        )

    def test_comment_creation(self):
        """Kiểm tra tạo bình luận."""
        self.assertEqual(self.comment.content, 'Bình luận test')
        self.assertEqual(self.comment.rating, 5)
        self.assertEqual(self.comment.resource, self.resource)

    def test_comment_str(self):
        """Kiểm tra __str__."""
        self.assertIn('commenter', str(self.comment))


class SubmissionLogTest(TestCase):
    """Test model SubmissionLog."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='admin123', role=User.Role.ADMIN
        )
        self.user = User.objects.create_user(
            username='author', password='testpass123', role=User.Role.USER
        )
        self.category = Category.objects.create(name='Vật lý')
        self.resource = Resource.objects.create(
            title='Cơ học',
            description='Mô tả',
            content='Nội dung',
            category=self.category,
            author=self.user,
        )

    def test_submission_log_creation(self):
        """Kiểm tra tạo nhật ký."""
        log = SubmissionLog.objects.create(
            resource=self.resource,
            reviewer=self.admin,
            old_status='pending',
            new_status='approved',
            note='Đã duyệt',
        )
        self.assertEqual(log.old_status, 'pending')
        self.assertEqual(log.new_status, 'approved')
        self.assertEqual(log.reviewer, self.admin)


class ResourceViewsTest(TestCase):
    """Test views tài liệu."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin', password='admin123', role=User.Role.ADMIN
        )
        self.user = User.objects.create_user(
            username='user', password='user123', role=User.Role.USER
        )
        self.category = Category.objects.create(
            name='Tin học', description='Tài liệu Tin học'
        )
        self.resource = Resource.objects.create(
            title='Python nâng cao',
            description='Mô tả tài liệu Python',
            content='Nội dung chi tiết',
            category=self.category,
            author=self.user,
            status='approved',
        )

    def test_resource_list(self):
        """Kiểm tra danh sách tài liệu."""
        response = self.client.get(reverse('resources:list'))
        self.assertEqual(response.status_code, 200)

    def test_resource_detail(self):
        """Kiểm tra chi tiết tài liệu."""
        response = self.client.get(
            reverse('resources:detail', args=[self.resource.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python nâng cao')

    def test_resource_create_requires_login(self):
        """Kiểm tra tạo tài liệu cần đăng nhập."""
        response = self.client.get(reverse('resources:create'))
        self.assertEqual(response.status_code, 302)

    def test_resource_create_user(self):
        """Kiểm tra user tạo tài liệu."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('resources:create'))
        self.assertEqual(response.status_code, 200)

    def test_resource_create_post(self):
        """Kiểm tra tạo tài liệu bằng POST."""
        self.client.login(username='user', password='user123')
        response = self.client.post(reverse('resources:create'), {
            'title': 'Django cơ bản',
            'description': 'Mô tả Django',
            'content': 'Nội dung Django',
            'category': self.category.id,
            'resource_type': 'document',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Resource.objects.filter(title='Django cơ bản').exists())

    def test_my_resources_requires_login(self):
        """Kiểm tra tài liệu của tôi cần đăng nhập."""
        response = self.client.get(reverse('resources:my_resources'))
        self.assertEqual(response.status_code, 302)

    def test_pending_resources_requires_admin(self):
        """Kiểm tra duyệt tài liệu cần quyền admin."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('resources:pending'))
        self.assertEqual(response.status_code, 302)

    def test_pending_resources_admin(self):
        """Kiểm tra admin xem tài liệu chờ duyệt."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('resources:pending'))
        self.assertEqual(response.status_code, 200)

    def test_approve_resource(self):
        """Kiểm tra phê duyệt tài liệu."""
        pending = Resource.objects.create(
            title='Tài liệu chờ',
            description='Mô tả',
            content='Nội dung',
            category=self.category,
            author=self.user,
            status='pending',
        )
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            reverse('resources:approve', args=[pending.pk])
        )
        self.assertEqual(response.status_code, 302)
        pending.refresh_from_db()
        self.assertEqual(pending.status, 'approved')

    def test_add_comment(self):
        """Kiểm tra thêm bình luận."""
        self.client.login(username='user', password='user123')
        response = self.client.post(
            reverse('resources:add_comment', args=[self.resource.slug]),
            {
                'content': 'Hay quá!',
                'rating': 5,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                resource=self.resource, content='Hay quá!'
            ).exists()
        )

    def test_search_resources(self):
        """Kiểm tra tìm kiếm tài liệu."""
        response = self.client.get(
            reverse('resources:list') + '?q=Python'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')

    def test_filter_by_category(self):
        """Kiểm tra lọc theo danh mục."""
        response = self.client.get(
            reverse('resources:list') + f'?category={self.category.id}'
        )
        self.assertEqual(response.status_code, 200)
