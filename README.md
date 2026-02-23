# EduResource - Thư viện Tài liệu Học tập

## 📋 Giới thiệu

**EduResource** là hệ thống quản lý và chia sẻ tài liệu học tập trực tuyến, được xây dựng bằng Django Framework. Hệ thống cho phép người dùng đăng tải, quản lý và tìm kiếm tài liệu học tập theo danh mục, với quy trình phê duyệt đảm bảo chất lượng nội dung.

## ✨ Tính năng chính

### 🔐 Quản lý người dùng
- Đăng ký / Đăng nhập / Đăng xuất
- Quản lý hồ sơ cá nhân (avatar, thông tin, bio)
- Phân quyền 3 vai trò: **Khách** / **Người dùng** / **Quản trị viên**
- Quên mật khẩu và đặt lại mật khẩu
- Admin quản lý và phân quyền người dùng

### 📚 Quản lý tài liệu
- CRUD tài liệu (Tạo, Xem, Sửa, Xóa)
- Phân loại theo danh mục và loại tài liệu
- Upload file đính kèm và ảnh minh họa
- Hệ thống trạng thái: Chờ duyệt → Đã duyệt / Từ chối
- Đếm lượt xem và lượt tải
- Nhật ký phê duyệt chi tiết

### 📂 Quản lý danh mục
- CRUD danh mục (Admin)
- Danh mục cha-con (phân cấp)
- Icon tùy chỉnh cho mỗi danh mục

### 🔍 Tìm kiếm & Lọc
- Tìm kiếm theo từ khóa
- Lọc theo danh mục, loại tài liệu
- Sắp xếp theo nhiều tiêu chí
- Phân trang danh sách

### 💬 Bình luận & Đánh giá
- Bình luận trên tài liệu
- Đánh giá sao (1-5 sao)
- Quản lý bình luận

### 📊 Dashboard & Báo cáo (Admin)
- Thống kê tổng quan (người dùng, tài liệu, lượt xem)
- Biểu đồ phân bố theo danh mục
- Biểu đồ trạng thái tài liệu
- Biểu đồ xu hướng theo tháng
- Top đóng góp viên

## 🛠 Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Django 4.2+ (Python) |
| Database | MySQL / SQLite |
| Frontend | Bootstrap 5.3, Font Awesome 6 |
| Charts | Chart.js 4.4 |
| Font | Google Fonts (Inter) |
| Auth | Django Authentication (Custom User Model) |

## 📁 Cấu trúc dự án

```
EduResources/
├── eduresource/          # Cấu hình project Django
│   ├── settings.py       # Cài đặt
│   ├── urls.py           # URL gốc
│   ├── views.py          # View trang chủ
│   ├── wsgi.py           # WSGI config
│   └── asgi.py           # ASGI config
├── accounts/             # App quản lý người dùng
│   ├── models.py         # Model User tùy chỉnh
│   ├── views.py          # Đăng nhập, đăng ký, profile
│   ├── forms.py          # Form xác thực
│   ├── decorators.py     # Decorator phân quyền
│   └── context_processors.py
├── categories/           # App quản lý danh mục
│   ├── models.py         # Model Category
│   ├── views.py          # CRUD danh mục
│   └── forms.py          # Form danh mục
├── resources/            # App quản lý tài liệu
│   ├── models.py         # Resource, Comment, SubmissionLog
│   ├── views.py          # CRUD, duyệt, bình luận
│   ├── forms.py          # Form tài liệu
│   └── management/       # Lệnh seed_data
├── dashboard/            # App dashboard admin
│   └── views.py          # Thống kê, báo cáo
├── templates/            # Template HTML
│   ├── base.html         # Layout chính
│   ├── home.html         # Trang chủ
│   ├── accounts/         # Template tài khoản
│   ├── resources/        # Template tài liệu
│   ├── categories/       # Template danh mục
│   └── dashboard/        # Template dashboard
├── static/               # File tĩnh
│   ├── css/style.css     # CSS tùy chỉnh
│   └── js/main.js        # JavaScript
├── media/                # File upload
├── manage.py             # Django CLI
├── requirements.txt      # Dependencies
├── .env                  # Biến môi trường
└── README.md             # Tài liệu dự án
```

## 🚀 Hướng dẫn cài đặt

### Yêu cầu
- Python 3.10+
- pip (Python package manager)
- MySQL 8.0+ (hoặc dùng SQLite mặc định)

### Bước 1: Clone dự án

```bash
git clone https://github.com/username/EduResources.git
cd EduResources
```

### Bước 2: Tạo môi trường ảo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình môi trường

Sao chép file `.env.example` thành `.env` và chỉnh sửa:

```bash
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac
```

Chỉnh sửa file `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# Sử dụng SQLite (mặc định)
DB_ENGINE=sqlite3

# Hoặc sử dụng MySQL
# DB_ENGINE=mysql
# DB_NAME=eduresource_db
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
```

### Bước 5: Chạy migrations

```bash
python manage.py makemigrations accounts
python manage.py makemigrations categories
python manage.py makemigrations resources
python manage.py migrate
```

### Bước 6: Tạo dữ liệu mẫu

```bash
python manage.py seed_data
```

### Bước 7: Chạy server

```bash
python manage.py runserver
```

Truy cập: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 👤 Tài khoản mẫu

| Vai trò | Tài khoản | Mật khẩu | Quyền hạn |
|---|---|---|---|
| Quản trị viên | `admin` | `admin123` | Toàn quyền quản lý |
| Người dùng 1 | `nguyenvana` | `user123` | Đăng tải, bình luận |
| Người dùng 2 | `tranthib` | `user123` | Đăng tải, bình luận |
| Người dùng 3 | `levanc` | `user123` | Đăng tải, bình luận |
| Người dùng 4 | `phamthid` | `user123` | Đăng tải, bình luận |
| Khách | `khach` | `guest123` | Chỉ xem |

## 📊 Mô hình dữ liệu

### Các thực thể chính (5+)

1. **User** - Người dùng (kế thừa AbstractUser)
   - Các trường: full_name, phone, avatar, bio, role
   - Vai trò: guest, user, admin

2. **Category** - Danh mục
   - Các trường: name, slug, description, icon, parent, is_active
   - Hỗ trợ phân cấp cha-con

3. **Resource** - Tài liệu
   - Các trường: title, slug, description, content, resource_type, category, author, file, thumbnail, status, view_count, download_count
   - Trạng thái: pending, approved, rejected

4. **Comment** - Bình luận
   - Các trường: resource, user, content, rating
   - Đánh giá 1-5 sao

5. **SubmissionLog** - Nhật ký phê duyệt
   - Các trường: resource, reviewer, old_status, new_status, note
   - Theo dõi quá trình duyệt tài liệu

### Quan hệ
- User (1) → (N) Resource (tác giả)
- Category (1) → (N) Resource
- Category (1) → (N) Category (cha-con)
- Resource (1) → (N) Comment
- Resource (1) → (N) SubmissionLog
- User (1) → (N) Comment
- User (1) → (N) SubmissionLog (người duyệt)

## 🔒 Phân quyền

| Chức năng | Khách | Người dùng | Admin |
|---|:---:|:---:|:---:|
| Xem trang chủ | ✅ | ✅ | ✅ |
| Xem danh sách tài liệu | ✅ | ✅ | ✅ |
| Xem chi tiết tài liệu | ✅ | ✅ | ✅ |
| Đăng tải tài liệu | ❌ | ✅ | ✅ |
| Sửa/Xóa tài liệu của mình | ❌ | ✅ | ✅ |
| Bình luận & đánh giá | ❌ | ✅ | ✅ |
| Quản lý danh mục | ❌ | ❌ | ✅ |
| Phê duyệt tài liệu | ❌ | ❌ | ✅ |
| Dashboard & Báo cáo | ❌ | ❌ | ✅ |
| Quản lý người dùng | ❌ | ❌ | ✅ |

## 🧪 Chạy Tests

```bash
python manage.py test
```

Hoặc chạy test từng app:
```bash
python manage.py test accounts
python manage.py test categories
python manage.py test resources
python manage.py test dashboard
```

## 📝 Quy trình nghiệp vụ

### Quy trình đăng tải tài liệu
1. Người dùng tạo tài liệu mới → Trạng thái: **Chờ duyệt**
2. Admin xem danh sách tài liệu chờ duyệt
3. Admin **Phê duyệt** → Trạng thái: **Đã duyệt** (hiển thị công khai)
4. Hoặc Admin **Từ chối** → Trạng thái: **Bị từ chối** (kèm lý do)
5. Mọi thay đổi trạng thái được ghi vào **Nhật ký phê duyệt**

## 📄 License

Dự án được phát triển cho mục đích học tập.

---

**EduResource** - Nền tảng chia sẻ tài liệu học tập © 2024
