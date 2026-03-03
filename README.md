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

| Thành phần | Công nghệ                                 |
| ---------- | ----------------------------------------- |
| Backend    | Django 4.2+ (Python)                      |
| Database   | MySQL / SQLite                            |
| Frontend   | Bootstrap 5.3, Font Awesome 6             |
| Charts     | Chart.js 4.4                              |
| Font       | Google Fonts (Inter)                      |
| Auth       | Django Authentication (Custom User Model) |

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

| Vai trò       | Tài khoản    | Mật khẩu   | Quyền hạn           |
| ------------- | ------------ | ---------- | ------------------- |
| Quản trị viên | `admin`      | `admin123` | Toàn quyền quản lý  |
| Người dùng 1  | `nguyenvana` | `user123`  | Đăng tải, bình luận |
| Người dùng 2  | `tranthib`   | `user123`  | Đăng tải, bình luận |
| Người dùng 3  | `levanc`     | `user123`  | Đăng tải, bình luận |
| Người dùng 4  | `phamthid`   | `user123`  | Đăng tải, bình luận |
| Khách         | `khach`      | `guest123` | Chỉ xem             |

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

| Chức năng                 | Khách | Người dùng | Admin |
| ------------------------- | :---: | :--------: | :---: |
| Xem trang chủ             |  ✅   |     ✅     |  ✅   |
| Xem danh sách tài liệu    |  ✅   |     ✅     |  ✅   |
| Xem chi tiết tài liệu     |  ✅   |     ✅     |  ✅   |
| Đăng tải tài liệu         |  ❌   |     ✅     |  ✅   |
| Sửa/Xóa tài liệu của mình |  ❌   |     ✅     |  ✅   |
| Bình luận & đánh giá      |  ❌   |     ✅     |  ✅   |
| Quản lý danh mục          |  ❌   |     ❌     |  ✅   |
| Phê duyệt tài liệu        |  ❌   |     ❌     |  ✅   |
| Dashboard & Báo cáo       |  ❌   |     ❌     |  ✅   |
| Quản lý người dùng        |  ❌   |     ❌     |  ✅   |

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

## � Tài liệu API

Hệ thống cung cấp các API endpoint (trả về JSON) phục vụ các tính năng real-time và AI.

### 1. API Xác thực & Tài khoản

| Method | Endpoint | Mô tả | Quyền | Rate Limit |
|--------|----------|-------|-------|------------|
| GET/POST | `/accounts/register/` | Đăng ký tài khoản | Public | 10 req/giờ (POST) |
| GET/POST | `/accounts/login/` | Đăng nhập | Public | 10 req/phút (POST) |
| GET | `/accounts/logout/` | Đăng xuất | Login | — |
| GET/POST | `/accounts/profile/` | Xem/cập nhật hồ sơ | Login | — |
| GET/POST | `/accounts/change-password/` | Đổi mật khẩu | Login | — |
| GET/POST | `/accounts/forgot-password/` | Quên mật khẩu | Public | 5 req/giờ (POST) |
| GET/POST | `/accounts/reset-password/<uidb64>/<token>/` | Đặt lại mật khẩu | Public (token) | — |
| GET | `/accounts/manage-users/` | Quản lý người dùng | Admin | — |
| POST | `/accounts/update-role/<user_id>/` | Cập nhật vai trò | Admin | — |

### 2. API Tài liệu (Resources)

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/resources/` | Danh sách tài liệu (tìm kiếm, lọc, sắp xếp, phân trang) | Public |
| GET/POST | `/resources/create/` | Tạo tài liệu mới | User/Admin |
| GET | `/resources/my/` | Tài liệu của tôi | Login |
| GET | `/resources/pending/` | Tài liệu chờ duyệt | Admin |
| GET | `/resources/<slug>/` | Chi tiết tài liệu | Public |
| GET/POST | `/resources/<slug>/edit/` | Sửa tài liệu | Tác giả/Admin |
| POST | `/resources/<slug>/delete/` | Xóa tài liệu | Tác giả/Admin |
| GET | `/resources/<slug>/download/` | Tải file tài liệu | Login |
| GET | `/resources/<slug>/preview/` | Xem trước file (PDF.js/mammoth) | Public |
| GET | `/resources/<slug>/file/` | Phục vụ file inline | Public |

**Query Parameters cho `/resources/`:**

| Param | Kiểu | Mô tả | Ví dụ |
|-------|------|-------|-------|
| `q` | string | Từ khóa tìm kiếm (tiêu đề, mô tả, nội dung) | `?q=python` |
| `category` | int | ID danh mục lọc | `?category=3` |
| `type` | string | Loại tài liệu (`document`, `video`, `image`, `audio`, `other`) | `?type=document` |
| `sort` | string | Sắp xếp (`-created_at`, `created_at`, `-view_count`, `title`, `-download_count`) | `?sort=-view_count` |
| `page` | int | Số trang (9 items/trang) | `?page=2` |

### 3. API Bình luận & Đánh giá

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| POST | `/resources/<slug>/comment/` | Thêm bình luận + đánh giá sao (1-5) | User/Admin |
| POST | `/resources/comment/<pk>/delete/` | Xóa bình luận | Tác giả bình luận/Admin |

### 4. API Phê duyệt tài liệu

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| POST | `/resources/<pk>/approve/` | Phê duyệt tài liệu (pending → approved) | Admin |
| POST | `/resources/<pk>/reject/` | Từ chối tài liệu (pending → rejected, kèm lý do) | Admin |

### 5. API Danh mục

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/categories/` | Danh sách danh mục (tìm kiếm, phân trang) | Public |
| GET/POST | `/categories/create/` | Tạo danh mục mới | Admin |
| GET/POST | `/categories/<pk>/edit/` | Sửa danh mục | Admin |
| POST | `/categories/<pk>/delete/` | Xóa danh mục (không cho xóa nếu có tài liệu) | Admin |

### 6. API Dashboard & Báo cáo

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/dashboard/` | Trang tổng quan (thống kê, pending, logs, top resources) | Admin |
| GET | `/dashboard/reports/` | Trang báo cáo (4 biểu đồ Chart.js + thống kê) | Admin |

### 7. API Thông báo Real-time (JSON)

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/api/notifications/` | Lấy danh sách thông báo + số chưa đọc | Login |
| POST | `/api/notifications/<pk>/read/` | Đánh dấu thông báo đã đọc | Login |
| POST | `/api/notifications/read-all/` | Đánh dấu tất cả đã đọc | Login |

**Response `/api/notifications/`:**
```json
{
  "unread_count": 3,
  "notifications": [
    {
      "id": 1,
      "type": "resource_approved",
      "title": "Tài liệu đã được duyệt",
      "message": "Tài liệu 'Python cơ bản' đã được phê duyệt.",
      "link": "/resources/python-co-ban/",
      "is_read": false,
      "icon_class": "fas fa-check-circle text-success",
      "created_at": "28/02/2026 10:30",
      "time_ago": "5 phút trước"
    }
  ]
}
```

### 8. API Tìm kiếm Tức thì (JSON)

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/api/search/?q=<keyword>` | Tìm kiếm real-time (debounce 300ms, tối thiểu 2 ký tự) | Public |

**Response `/api/search/?q=python`:**
```json
{
  "results": [
    {
      "title": "Python cơ bản",
      "slug": "python-co-ban",
      "category": "Tin học",
      "author": "Nguyễn Văn A",
      "type": "Tài liệu",
      "type_raw": "document",
      "view_count": 150,
      "rating": 4.5,
      "thumbnail": "/media/resources/thumbnails/python.jpg",
      "created_at": "15/01/2026"
    }
  ],
  "total": 5,
  "query": "python"
}
```

### 9. API Online Users & Dashboard Stats (JSON)

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/api/online-users/` | Số người đang online (active trong 5 phút) | Public |
| GET | `/api/dashboard-stats/` | Thống kê real-time cho dashboard | Admin |

**Response `/api/online-users/`:**
```json
{
  "online_count": 12
}
```

**Response `/api/dashboard-stats/`:**
```json
{
  "total_resources": 45,
  "total_users": 20,
  "pending_resources": 3,
  "approved_resources": 38,
  "rejected_resources": 4,
  "total_downloads": 1250,
  "total_views": 8900,
  "total_comments": 120,
  "online_count": 12
}
```

### 10. API Tính năng AI (JSON)

| Method | Endpoint | Mô tả | Quyền | Rate Limit |
|--------|----------|-------|-------|------------|
| POST | `/api/ai/summarize/<slug>/` | Tóm tắt tài liệu bằng AI (Gemini) | Login | 20 req/giờ |
| POST | `/api/ai/chat/<slug>/` | Chatbot hỏi đáp về tài liệu | Login | 60 req/giờ |
| POST | `/api/ai/suggest-tags/` | Gợi ý danh mục & tags cho tài liệu | Login | — |

**Request `/api/ai/chat/<slug>/`:**
```json
{
  "message": "Tài liệu này nói về gì?",
  "history": [
    {"role": "user", "content": "Xin chào"},
    {"role": "assistant", "content": "Chào bạn! Tôi có thể giúp gì?"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "reply": "Tài liệu này trình bày về các khái niệm cơ bản..."
}
```

**Request `/api/ai/suggest-tags/`:**
```json
{
  "title": "Giáo trình Python",
  "description": "Tài liệu học Python cơ bản",
  "content": "Nội dung chi tiết...",
  "resource_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "suggestions": {
    "category": "Tin học",
    "tags": ["python", "lập trình", "cơ bản"]
  }
}
```

### Mã lỗi HTTP

| Code | Ý nghĩa | Trang lỗi |
|------|---------|-----------|
| 200 | Thành công | — |
| 302 | Chuyển hướng (redirect) | — |
| 400 | Dữ liệu không hợp lệ | JSON `{"success": false, "error": "..."}` |
| 403 | Không có quyền truy cập | Trang 403 tùy chỉnh |
| 404 | Không tìm thấy | Trang 404 tùy chỉnh |
| 429 | Vượt giới hạn rate limit | Trang 429 tùy chỉnh |
| 500 | Lỗi server | Trang 500 tùy chỉnh |

## �📝 Quy trình nghiệp vụ

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
