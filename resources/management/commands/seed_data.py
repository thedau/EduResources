"""
Lệnh quản lý tùy chỉnh - Tạo dữ liệu mẫu cho EduResource.
Sử dụng: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from categories.models import Category
from resources.models import Resource, Comment, SubmissionLog
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho hệ thống EduResource'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Bắt đầu tạo dữ liệu mẫu...'))

        # === 1. TẠO NGƯỜI DÙNG ===
        self.stdout.write('Tạo người dùng...')

        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'full_name': 'Quản trị viên',
                'email': 'admin@eduresource.vn',
                'role': User.Role.ADMIN,
                'phone': '0901234567',
                'bio': 'Quản trị viên hệ thống EduResource',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Admin: admin / admin123'))

        # Giảng viên 1
        teacher1, created = User.objects.get_or_create(
            username='nguyenvana',
            defaults={
                'full_name': 'Nguyễn Văn A',
                'email': 'nguyenvana@edu.vn',
                'role': User.Role.USER,
                'phone': '0912345678',
                'bio': 'Giảng viên Toán học - Đại học Bách Khoa',
            }
        )
        if created:
            teacher1.set_password('user123')
            teacher1.save()
            self.stdout.write(self.style.SUCCESS('  ✓ User: nguyenvana / user123'))

        # Giảng viên 2
        teacher2, created = User.objects.get_or_create(
            username='tranthib',
            defaults={
                'full_name': 'Trần Thị B',
                'email': 'tranthib@edu.vn',
                'role': User.Role.USER,
                'phone': '0923456789',
                'bio': 'Giảng viên Vật lý - Đại học Khoa học Tự nhiên',
            }
        )
        if created:
            teacher2.set_password('user123')
            teacher2.save()
            self.stdout.write(self.style.SUCCESS('  ✓ User: tranthib / user123'))

        # Sinh viên 1
        student1, created = User.objects.get_or_create(
            username='levanc',
            defaults={
                'full_name': 'Lê Văn C',
                'email': 'levanc@edu.vn',
                'role': User.Role.USER,
                'phone': '0934567890',
                'bio': 'Sinh viên năm 3 - Công nghệ thông tin',
            }
        )
        if created:
            student1.set_password('user123')
            student1.save()
            self.stdout.write(self.style.SUCCESS('  ✓ User: levanc / user123'))

        # Sinh viên 2
        student2, created = User.objects.get_or_create(
            username='phamthid',
            defaults={
                'full_name': 'Phạm Thị D',
                'email': 'phamthid@edu.vn',
                'role': User.Role.USER,
                'phone': '0945678901',
                'bio': 'Sinh viên năm 2 - Kinh tế',
            }
        )
        if created:
            student2.set_password('user123')
            student2.save()
            self.stdout.write(self.style.SUCCESS('  ✓ User: phamthid / user123'))

        # Guest
        guest, created = User.objects.get_or_create(
            username='khach',
            defaults={
                'full_name': 'Người dùng khách',
                'email': 'guest@eduresource.vn',
                'role': User.Role.GUEST,
            }
        )
        if created:
            guest.set_password('guest123')
            guest.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Guest: khach / guest123'))

        users = [teacher1, teacher2, student1, student2]

        # === 2. TẠO DANH MỤC ===
        self.stdout.write('Tạo danh mục...')

        categories_data = [
            {'name': 'Toán học', 'icon': 'fas fa-calculator', 'description': 'Tài liệu về Đại số, Giải tích, Xác suất thống kê và các chuyên ngành Toán'},
            {'name': 'Vật lý', 'icon': 'fas fa-atom', 'description': 'Tài liệu về Cơ học, Điện từ, Quang học và Vật lý hiện đại'},
            {'name': 'Hóa học', 'icon': 'fas fa-flask', 'description': 'Tài liệu về Hóa vô cơ, Hóa hữu cơ, Hóa phân tích và Hóa lý'},
            {'name': 'Sinh học', 'icon': 'fas fa-dna', 'description': 'Tài liệu về Sinh học phân tử, Di truyền, Sinh thái và Tiến hóa'},
            {'name': 'Tin học', 'icon': 'fas fa-laptop-code', 'description': 'Tài liệu về Lập trình, Cơ sở dữ liệu, Mạng máy tính và AI'},
            {'name': 'Ngữ văn', 'icon': 'fas fa-book-open', 'description': 'Tài liệu về Văn học Việt Nam và thế giới, Ngôn ngữ học'},
            {'name': 'Tiếng Anh', 'icon': 'fas fa-language', 'description': 'Tài liệu học Tiếng Anh: Ngữ pháp, Từ vựng, IELTS, TOEIC'},
            {'name': 'Lịch sử', 'icon': 'fas fa-landmark', 'description': 'Tài liệu về Lịch sử Việt Nam và Lịch sử thế giới'},
            {'name': 'Địa lý', 'icon': 'fas fa-globe-asia', 'description': 'Tài liệu về Địa lý tự nhiên, Địa lý kinh tế - xã hội'},
            {'name': 'Kinh tế', 'icon': 'fas fa-chart-line', 'description': 'Tài liệu về Kinh tế vi mô, Kinh tế vĩ mô, Tài chính và Quản trị'},
        ]

        categories = []
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data['description'],
                    'is_active': True,
                }
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'  ✓ Danh mục: {cat.name}')

        # === 3. TẠO TÀI LIỆU ===
        self.stdout.write('Tạo tài liệu...')

        resources_data = [
            # Toán học
            {
                'title': 'Giáo trình Giải tích 1',
                'description': 'Giáo trình Giải tích 1 dành cho sinh viên năm nhất các ngành kỹ thuật',
                'content': 'Giáo trình bao gồm các chương: Số thực và dãy số, Hàm số một biến, Giới hạn và liên tục, Đạo hàm và vi phân, Tích phân, Chuỗi số và chuỗi hàm. Mỗi chương có lý thuyết chi tiết, ví dụ minh họa và bài tập đa dạng.',
                'category': 'Toán học',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 1250,
                'download_count': 340,
            },
            {
                'title': 'Bài tập Xác suất thống kê có lời giải',
                'description': 'Tuyển tập bài tập Xác suất thống kê từ cơ bản đến nâng cao',
                'content': 'Tuyển tập gồm 200 bài tập được phân loại theo chương, có đáp án và hướng dẫn giải chi tiết. Phù hợp cho sinh viên ôn thi.',
                'category': 'Toán học',
                'resource_type': 'exercise',
                'status': 'approved',
                'view_count': 890,
                'download_count': 210,
            },
            # Vật lý
            {
                'title': 'Vật lý đại cương - Cơ học',
                'description': 'Slide bài giảng Vật lý đại cương phần Cơ học Newton',
                'content': 'Bộ slide bài giảng gồm 10 chương về Cơ học cổ điển: Động học chất điểm, Động lực học, Công và năng lượng, Xung lượng và động lượng, Chuyển động quay, Dao động và sóng cơ.',
                'category': 'Vật lý',
                'resource_type': 'presentation',
                'status': 'approved',
                'view_count': 750,
                'download_count': 180,
            },
            {
                'title': 'Thí nghiệm Vật lý - Báo cáo mẫu',
                'description': 'Mẫu báo cáo thí nghiệm Vật lý đại cương cho sinh viên',
                'content': 'Hướng dẫn viết báo cáo thí nghiệm chuẩn, bao gồm các bài thí nghiệm: Con lắc đơn, Đo gia tốc trọng trường, Hiệu ứng quang điện...',
                'category': 'Vật lý',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 520,
                'download_count': 150,
            },
            # Tin học
            {
                'title': 'Lập trình Python cơ bản',
                'description': 'Tài liệu học Python từ đầu dành cho người mới bắt đầu',
                'content': 'Khóa học bao gồm: Cài đặt môi trường, Biến và kiểu dữ liệu, Cấu trúc điều khiển, Hàm, OOP, Xử lý file, Thư viện phổ biến. Có nhiều ví dụ thực hành và dự án mini.',
                'category': 'Tin học',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 2100,
                'download_count': 560,
            },
            {
                'title': 'Cấu trúc dữ liệu và giải thuật',
                'description': 'Giáo trình CTDL&GT bằng ngôn ngữ C++',
                'content': 'Nội dung: Mảng, Danh sách liên kết, Stack, Queue, Cây nhị phân, Đồ thị, Sắp xếp, Tìm kiếm, Quy hoạch động. Mỗi chương có code minh họa và bài tập.',
                'category': 'Tin học',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 1800,
                'download_count': 420,
            },
            {
                'title': 'Hướng dẫn Git và GitHub',
                'description': 'Tài liệu học Git cơ bản đến nâng cao cho sinh viên IT',
                'content': 'Bao gồm: Khái niệm cơ bản, Cài đặt và cấu hình, Các lệnh thường dùng, Branching, Merging, Pull Request, Giải quyết conflict, Git Flow.',
                'category': 'Tin học',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 1500,
                'download_count': 380,
            },
            # Tiếng Anh
            {
                'title': 'IELTS Writing Task 2 - Tổng hợp đề và bài mẫu',
                'description': 'Tuyển tập 50 đề thi IELTS Writing Task 2 kèm bài mẫu band 7+',
                'content': 'Tuyển tập gồm 50 đề thi thường gặp trong IELTS Writing Task 2, được phân loại theo chủ đề: Education, Technology, Health, Environment, Society. Mỗi đề kèm bài mẫu, phân tích cấu trúc và từ vựng nâng cao.',
                'category': 'Tiếng Anh',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 3200,
                'download_count': 890,
            },
            {
                'title': 'Ngữ pháp Tiếng Anh toàn tập',
                'description': 'Tổng hợp ngữ pháp Tiếng Anh từ cơ bản đến nâng cao',
                'content': 'Bao gồm đầy đủ các chủ đề ngữ pháp: Thì, Câu điều kiện, Mệnh đề quan hệ, Câu bị động, Liên từ, Giới từ, Mạo từ, Danh từ đếm được/không đếm được...',
                'category': 'Tiếng Anh',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 2800,
                'download_count': 720,
            },
            # Kinh tế
            {
                'title': 'Kinh tế vi mô - Slide bài giảng',
                'description': 'Bộ slide bài giảng Kinh tế vi mô cho sinh viên Kinh tế',
                'content': 'Gồm các chương: Cung cầu, Co giãn, Lý thuyết hành vi người tiêu dùng, Lý thuyết sản xuất, Chi phí sản xuất, Cấu trúc thị trường, Thất bại thị trường.',
                'category': 'Kinh tế',
                'resource_type': 'presentation',
                'status': 'approved',
                'view_count': 640,
                'download_count': 160,
            },
            # Hóa học
            {
                'title': 'Hóa học đại cương - Bảng tuần hoàn',
                'description': 'Tài liệu chi tiết về Bảng tuần hoàn các nguyên tố hóa học',
                'content': 'Tài liệu trình bày chi tiết về cấu tạo bảng tuần hoàn, tính chất của các nhóm nguyên tố, quy luật biến đổi tính chất theo chu kỳ và nhóm.',
                'category': 'Hóa học',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 430,
                'download_count': 120,
            },
            # Sinh học
            {
                'title': 'Sinh học phân tử - ADN và Gen',
                'description': 'Tài liệu về cấu trúc ADN, quá trình nhân đôi và biểu hiện gen',
                'content': 'Nội dung bao gồm: Cấu trúc ADN, ARN, Quá trình nhân đôi ADN, Phiên mã, Dịch mã, Đột biến gen, Công nghệ gen.',
                'category': 'Sinh học',
                'resource_type': 'document',
                'status': 'approved',
                'view_count': 380,
                'download_count': 95,
            },
            # Tài liệu chờ duyệt
            {
                'title': 'Machine Learning cho người mới bắt đầu',
                'description': 'Giới thiệu Machine Learning và các thuật toán cơ bản',
                'content': 'Tài liệu giới thiệu lĩnh vực Machine Learning, bao gồm: Regression, Classification, Clustering, Neural Networks, Deep Learning. Có ví dụ code bằng Python.',
                'category': 'Tin học',
                'resource_type': 'document',
                'status': 'pending',
                'view_count': 0,
                'download_count': 0,
            },
            {
                'title': 'Lịch sử Việt Nam thời kỳ đổi mới',
                'description': 'Tổng quan về thời kỳ đổi mới của Việt Nam từ 1986 đến nay',
                'content': 'Tài liệu trình bày bối cảnh, nguyên nhân, quá trình đổi mới và các thành tựu nổi bật của Việt Nam trong giai đoạn 1986 đến nay.',
                'category': 'Lịch sử',
                'resource_type': 'document',
                'status': 'pending',
                'view_count': 0,
                'download_count': 0,
            },
            # Tài liệu bị từ chối
            {
                'title': 'Tài liệu ôn thi không rõ nguồn',
                'description': 'Tổng hợp đề thi các môn',
                'content': 'Nội dung chưa được kiểm chứng.',
                'category': 'Toán học',
                'resource_type': 'document',
                'status': 'rejected',
                'view_count': 0,
                'download_count': 0,
            },
        ]

        for i, res_data in enumerate(resources_data):
            cat = Category.objects.get(name=res_data['category'])
            author = users[i % len(users)]
            days_ago = random.randint(1, 180)

            resource, created = Resource.objects.get_or_create(
                title=res_data['title'],
                defaults={
                    'description': res_data['description'],
                    'content': res_data['content'],
                    'category': cat,
                    'author': author,
                    'resource_type': res_data['resource_type'],
                    'status': res_data['status'],
                    'view_count': res_data['view_count'],
                    'download_count': res_data['download_count'],
                }
            )
            if created:
                # Cập nhật ngày tạo
                resource.created_at = timezone.now() - timedelta(days=days_ago)
                resource.save(update_fields=['created_at'])

                # Tạo nhật ký
                if res_data['status'] == 'approved':
                    SubmissionLog.objects.create(
                        resource=resource,
                        reviewer=admin,
                        old_status='pending',
                        new_status='approved',
                        note='Tài liệu đã được phê duyệt'
                    )
                elif res_data['status'] == 'rejected':
                    SubmissionLog.objects.create(
                        resource=resource,
                        reviewer=admin,
                        old_status='pending',
                        new_status='rejected',
                        note='Nội dung chưa đạt yêu cầu chất lượng'
                    )

                self.stdout.write(f'  ✓ Tài liệu: {resource.title[:50]}')

        # === 4. TẠO BÌNH LUẬN ===
        self.stdout.write('Tạo bình luận...')

        approved_resources = Resource.objects.filter(status='approved')
        comments_data = [
            'Tài liệu rất hay và chi tiết, cảm ơn tác giả!',
            'Nội dung dễ hiểu, rất phù hợp để ôn thi.',
            'Tuyệt vời! Đây là tài liệu tôi đang tìm kiếm.',
            'Cảm ơn bạn đã chia sẻ tài liệu hữu ích này.',
            'Tài liệu khá tốt, nhưng có thể bổ sung thêm ví dụ.',
            'Rất bổ ích cho sinh viên năm nhất.',
            'Slide trình bày đẹp và dễ theo dõi.',
            'Mình đã dùng tài liệu này để ôn thi và đạt điểm cao.',
            'Nội dung cập nhật và phong phú.',
            'Cảm ơn, tài liệu rất giá trị cho việc học tập.',
        ]

        for resource in approved_resources:
            num_comments = random.randint(1, 4)
            for j in range(num_comments):
                commenter = random.choice(users)
                comment_text = random.choice(comments_data)
                rating = random.randint(3, 5)

                Comment.objects.get_or_create(
                    resource=resource,
                    user=commenter,
                    content=comment_text,
                    defaults={
                        'rating': rating,
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo bình luận'))

        # === KẾT QUẢ ===
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('DỮ LIỆU MẪU ĐÃ ĐƯỢC TẠO THÀNH CÔNG!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Tài khoản mẫu:')
        self.stdout.write(f'  Admin:     admin / admin123')
        self.stdout.write(f'  User 1:    nguyenvana / user123')
        self.stdout.write(f'  User 2:    tranthib / user123')
        self.stdout.write(f'  User 3:    levanc / user123')
        self.stdout.write(f'  User 4:    phamthid / user123')
        self.stdout.write(f'  Guest:     khach / guest123')
        self.stdout.write('')
        self.stdout.write(f'Thống kê:')
        self.stdout.write(f'  Người dùng:  {User.objects.count()}')
        self.stdout.write(f'  Danh mục:    {Category.objects.count()}')
        self.stdout.write(f'  Tài liệu:   {Resource.objects.count()}')
        self.stdout.write(f'  Bình luận:   {Comment.objects.count()}')
        self.stdout.write('')
