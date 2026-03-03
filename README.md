# EduResource - Thư viện Tài liệu Học tập Trực tuyến

## 📋 Giới thiệu

**EduResource** là hệ thống quản lý và chia sẻ tài liệu học tập trực tuyến, được xây dựng bằng **Django Framework**. Hệ thống cho phép người dùng đăng tải, quản lý và tìm kiếm tài liệu học tập theo danh mục, với quy trình phê duyệt đảm bảo chất lượng nội dung. Tích hợp **AI (Groq LLaMA 3.3)** để tóm tắt tài liệu, chatbot hỗ trợ học tập, và gợi ý phân loại tự động.

## ✨ Tính năng chính

### 🔐 Quản lý người dùng
- Đăng ký / Đăng nhập / Đăng xuất
- Quản lý hồ sơ cá nhân (avatar, thông tin, bio)
- Phân quyền 3 vai trò: **Khách** / **Người dùng** / **Quản trị viên**
- Đổi mật khẩu, quên mật khẩu và đặt lại mật khẩu (token-based)
- Admin quản lý và phân quyền người dùng

### 📚 Quản lý tài liệu
- CRUD tài liệu (Tạo, Xem, Sửa, Xóa)
- Phân loại theo danh mục và loại tài liệu (Tài liệu, Video, Bài trình bày, Bài tập, Khác)
- Upload file đính kèm (PDF, DOCX, PPTX, XLSX, ZIP...) và ảnh thumbnail
- Xem trước file trực tiếp trên trình duyệt (PDF.js cho PDF, mammoth cho DOCX)
- Quy trình duyệt: **Chờ duyệt → Đã duyệt / Từ chối** (kèm lý do)
- Đếm lượt xem (atomic, chống trùng bằng session) và lượt tải xuống
- Nhật ký phê duyệt chi tiết (SubmissionLog)
- Tự động sinh slug từ tiêu đề tiếng Việt (unidecode)

### 📂 Quản lý danh mục
- CRUD danh mục (Admin)
- Danh mục phân cấp cha-con (self-referencing FK)
- Icon tùy chỉnh Font Awesome cho mỗi danh mục
- Bảo vệ xóa: không cho xóa danh mục có tài liệu

### 🔍 Tìm kiếm & Lọc
- Tìm kiếm theo từ khóa (tiêu đề, mô tả, nội dung)
- Tìm kiếm tức thì (Live Search) với AJAX debounce 300ms
- Lọc theo danh mục, loại tài liệu
- Sắp xếp: mới nhất, cũ nhất, nhiều lượt xem, nhiều lượt tải, theo tên
- Phân trang danh sách

### 💬 Bình luận & Đánh giá
- Bình luận trên tài liệu kèm đánh giá sao (1-5)
- Tính điểm trung bình tự động
- Xóa bình luận (tác giả hoặc Admin)

### 🔔 Thông báo Real-time
- Thông báo tự động khi: tài liệu được duyệt/từ chối, có bình luận mới, tài liệu mới chờ duyệt
- AJAX polling mỗi 15 giây
- Đánh dấu đã đọc (từng thông báo hoặc tất cả)
- Hiển thị số người đang online (UserActivity tracking)

### 📊 Dashboard & Báo cáo (Admin)
- Thống kê tổng quan (người dùng, tài liệu, lượt xem, lượt tải, bình luận)
- Biểu đồ cột: phân bố tài liệu theo danh mục
- Biểu đồ tròn: trạng thái tài liệu
- Biểu đồ đường: xu hướng tài liệu theo tháng (12 tháng gần nhất)
- Biểu đồ ngang: top người đóng góp
- Live dashboard stats (cập nhật mỗi 30 giây)

### 🤖 Tích hợp AI (Groq LLaMA 3.3 70B)
- **Tóm tắt tài liệu**: Trích xuất nội dung từ file (PDF/DOCX/TXT) rồi tóm tắt bằng AI
- **Chatbot trợ giảng**: Hỏi đáp về nội dung tài liệu cụ thể (có lịch sử hội thoại)
- **Gợi ý phân loại**: AI đề xuất danh mục, loại tài liệu, và tags phù hợp
- **Chatbot tổng quát (EduBot)**: Widget chatbot nổi trên toàn bộ website, hỗ trợ tìm tài liệu, hướng dẫn sử dụng

### 🎨 Giao diện
- Responsive design (Bootstrap 5.3)
- Hỗ trợ Dark mode
- Navbar glassmorphism trên mobile
- Chatbot widget nổi (floating)
- Trang lỗi tùy chỉnh (403, 404, 429, 500)

## 🛠 Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Django 4.2 (Python 3.12) |
| Database | MySQL 8.0 |
| Frontend | Bootstrap 5.3, Font Awesome 6, Google Fonts (Inter) |
| Charts | Chart.js 4.4 |
| AI | Groq API (LLaMA 3.3 70B Versatile) |
| File Processing | PyPDF2 (PDF), mammoth (DOCX), PDF.js (preview) |
| Real-time | AJAX Polling (Fetch API) |
| Rate Limiting | django-ratelimit |
| Caching | Django LocMemCache |
| Security | CSRF, Rate Limiting, Token-based Password Reset |

## 📁 Cấu trúc dự án

```
EduResources/
├── eduresource/              # Cấu hình project Django
│   ├── settings.py           # Cài đặt (DB, cache, security, Groq API)
│   ├── urls.py               # URL gốc + error handlers
│   ├── views.py              # Trang chủ + custom error pages
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
├── accounts/                 # App quản lý người dùng
│   ├── models.py             # Model User tùy chỉnh (AbstractUser)
│   ├── views.py              # Đăng nhập, đăng ký, profile, quản lý users
│   ├── forms.py              # RegisterForm, LoginForm, ProfileForm, ...
│   ├── decorators.py         # @admin_required, @authenticated_required
│   └── context_processors.py # user_role context (pending_count cache)
├── categories/               # App quản lý danh mục
│   ├── models.py             # Model Category (self-referencing)
│   ├── views.py              # CRUD danh mục
│   └── forms.py              # CategoryForm
├── resources/                # App quản lý tài liệu
│   ├── models.py             # Resource, Comment, SubmissionLog
│   ├── views.py              # CRUD, duyệt, bình luận, download, preview
│   ├── forms.py              # ResourceForm, CommentForm, ResourceRejectForm
│   ├── templatetags/         # Custom template filter (rating_display)
│   └── management/commands/  # seed_data command
├── dashboard/                # App dashboard & báo cáo (Admin)
│   └── views.py              # Thống kê tổng quan + biểu đồ Chart.js
├── notifications/            # App thông báo real-time
│   ├── models.py             # Notification, UserActivity
│   ├── views.py              # API: notifications, live search, online users
│   ├── signals.py            # Auto-create notifications on events
│   └── middleware.py         # OnlineUsersMiddleware (last_seen tracking)
├── ai_features/              # App tính năng AI
│   ├── services.py           # Groq API: summarize, chat, suggest, general_chat
│   ├── views.py              # API endpoints cho AI features
│   └── urls.py               # 4 API routes
├── templates/                # Template HTML
│   ├── base.html             # Layout chính + chatbot widget
│   ├── home.html             # Trang chủ
│   ├── 403.html, 404.html,   # Trang lỗi tùy chỉnh
│   │   429.html, 500.html
│   ├── accounts/             # 7 template: login, register, profile, ...
│   ├── resources/            # 6 template: list, detail, form, preview, ...
│   ├── categories/           # 2 template: list, form
│   └── dashboard/            # 2 template: index, reports
├── static/
│   ├── css/style.css         # CSS tùy chỉnh (~2000 dòng, dark mode)
│   └── js/
│       ├── main.js           # JS chính + chatbot widget (~480 dòng)
│       └── realtime.js       # AJAX polling: notifications, search, online (~350 dòng)
├── media/                    # File upload (avatars, resources)
├── manage.py
├── requirements.txt
├── .env                      # Biến môi trường (SECRET_KEY, DB, GROQ_API_KEY)
└── README.md
```

## 🚀 Hướng dẫn cài đặt

### Yêu cầu
- Python 3.10+
- pip (Python package manager)
- MySQL 8.0+

### Bước 1: Clone dự án

```bash
git clone https://github.com/username/EduResources.git
cd EduResources
```

### Bước 2: Tạo môi trường ảo

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
pip install groq
```

### Bước 4: Cấu hình môi trường

Tạo file `.env` tại thư mục gốc:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# === Database (MySQL) ===
DB_NAME=eduresource
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# === AI (Groq) ===
GROQ_API_KEY=your_groq_api_key_here
```

> 💡 Lấy Groq API key miễn phí tại: https://console.groq.com/keys

### Bước 5: Chạy migrations

```bash
python manage.py makemigrations accounts categories resources notifications
python manage.py migrate
```

### Bước 6: Tạo dữ liệu mẫu

```bash
python manage.py seed_data
```

### Bước 7: Thu thập file tĩnh

```bash
python manage.py collectstatic --noinput
```

### Bước 8: Chạy server

```bash
python manage.py runserver
```

Truy cập: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 👤 Tài khoản mẫu

| Vai trò | Tài khoản | Mật khẩu | Quyền hạn |
|---------|-----------|----------|-----------|
| Quản trị viên | `admin` | `admin123` | Toàn quyền quản lý |
| Người dùng 1 | `nguyenvana` | `user123` | Đăng tải, bình luận |
| Người dùng 2 | `tranthib` | `user123` | Đăng tải, bình luận |
| Người dùng 3 | `levanc` | `user123` | Đăng tải, bình luận |
| Người dùng 4 | `phamthid` | `user123` | Đăng tải, bình luận |
| Khách | `khach` | `guest123` | Chỉ xem |

## 📊 Mô hình dữ liệu

### Các thực thể (7 bảng)

| # | Thực thể | App | Mô tả |
|---|----------|-----|-------|
| 1 | **User** | accounts | Người dùng (kế thừa AbstractUser), 3 vai trò: guest/user/admin |
| 2 | **Category** | categories | Danh mục phân cấp cha-con (self-referencing FK) |
| 3 | **Resource** | resources | Tài liệu học tập - thực thể trung tâm |
| 4 | **Comment** | resources | Bình luận + đánh giá sao (1-5) |
| 5 | **SubmissionLog** | resources | Nhật ký quy trình duyệt tài liệu |
| 6 | **Notification** | notifications | Thông báo real-time cho người dùng |
| 7 | **UserActivity** | notifications | Theo dõi trạng thái online (last_seen) |

### Quan hệ giữa các thực thể

| Quan hệ | Kiểu | Mô tả |
|---------|------|-------|
| User → Resource | 1:N | Một người dùng tạo nhiều tài liệu |
| User → Comment | 1:N | Một người dùng viết nhiều bình luận |
| User → Notification | 1:N | Một người dùng nhận nhiều thông báo |
| User → UserActivity | 1:1 | Mỗi người dùng có một bản ghi hoạt động |
| User → SubmissionLog | 1:N | Một admin duyệt nhiều tài liệu |
| Category → Resource | 1:N | Một danh mục chứa nhiều tài liệu |
| Category → Category | 1:N | Danh mục cha chứa nhiều danh mục con |
| Resource → Comment | 1:N | Một tài liệu có nhiều bình luận |
| Resource → SubmissionLog | 1:N | Một tài liệu có nhiều bản ghi duyệt |

## 🔒 Phân quyền

| Chức năng | Khách | Người dùng | Admin |
|-----------|:-----:|:----------:|:-----:|
| Xem trang chủ, danh sách, chi tiết tài liệu | ✅ | ✅ | ✅ |
| Tìm kiếm, lọc tài liệu | ✅ | ✅ | ✅ |
| Đăng tải tài liệu | ❌ | ✅ | ✅ |
| Sửa/Xóa tài liệu của mình | ❌ | ✅ | ✅ |
| Tải xuống file đính kèm | ❌ | ✅ | ✅ |
| Bình luận & đánh giá | ❌ | ✅ | ✅ |
| Sử dụng AI (tóm tắt, chatbot) | ❌ | ✅ | ✅ |
| Nhận thông báo | ❌ | ✅ | ✅ |
| Quản lý danh mục (CRUD) | ❌ | ❌ | ✅ |
| Phê duyệt / Từ chối tài liệu | ❌ | ❌ | ✅ |
| Dashboard & Báo cáo thống kê | ❌ | ❌ | ✅ |
| Quản lý người dùng & phân quyền | ❌ | ❌ | ✅ |

## 📡 API Endpoints

### Tài khoản

| Method | Endpoint | Mô tả | Quyền | Rate Limit |
|--------|----------|-------|-------|------------|
| GET/POST | `/accounts/register/` | Đăng ký | Public | 10/giờ |
| GET/POST | `/accounts/login/` | Đăng nhập | Public | 10/phút |
| GET | `/accounts/logout/` | Đăng xuất | Login | — |
| GET/POST | `/accounts/profile/` | Hồ sơ cá nhân | Login | — |
| GET/POST | `/accounts/change-password/` | Đổi mật khẩu | Login | — |
| GET/POST | `/accounts/forgot-password/` | Quên mật khẩu | Public | 5/giờ |
| GET/POST | `/accounts/reset-password/<uidb64>/<token>/` | Đặt lại mật khẩu | Token | — |
| GET | `/accounts/manage-users/` | Quản lý người dùng | Admin | — |
| POST | `/accounts/update-role/<user_id>/` | Cập nhật vai trò | Admin | — |

### Tài liệu

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/resources/` | Danh sách (tìm kiếm, lọc, sắp xếp, phân trang) | Public |
| GET/POST | `/resources/create/` | Tạo tài liệu | Login |
| GET | `/resources/my/` | Tài liệu của tôi | Login |
| GET | `/resources/pending/` | Chờ duyệt | Admin |
| GET | `/resources/<slug>/` | Chi tiết | Public |
| GET/POST | `/resources/<slug>/edit/` | Sửa | Tác giả/Admin |
| POST | `/resources/<slug>/delete/` | Xóa | Tác giả/Admin |
| GET | `/resources/<slug>/download/` | Tải file | Login |
| GET | `/resources/<slug>/preview/` | Xem trước (PDF.js/mammoth) | Public |
| POST | `/resources/<slug>/comment/` | Thêm bình luận | Login |
| POST | `/resources/<pk>/approve/` | Phê duyệt | Admin |
| POST | `/resources/<pk>/reject/` | Từ chối | Admin |

### Danh mục

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/categories/` | Danh sách (tìm kiếm, phân trang) | Public |
| GET/POST | `/categories/create/` | Tạo mới | Admin |
| GET/POST | `/categories/<pk>/edit/` | Sửa | Admin |
| POST | `/categories/<pk>/delete/` | Xóa | Admin |

### Dashboard

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/dashboard/` | Tổng quan | Admin |
| GET | `/dashboard/reports/` | Báo cáo (4 biểu đồ Chart.js) | Admin |

### Thông báo & Real-time (JSON API)

| Method | Endpoint | Mô tả | Quyền |
|--------|----------|-------|-------|
| GET | `/api/notifications/` | Danh sách thông báo + số chưa đọc | Login |
| POST | `/api/notifications/<pk>/read/` | Đánh dấu đã đọc | Login |
| POST | `/api/notifications/read-all/` | Đánh dấu tất cả đã đọc | Login |
| GET | `/api/search/?q=<keyword>` | Tìm kiếm tức thì | Public |
| GET | `/api/online-users/` | Số người đang online | Public |
| GET | `/api/dashboard-stats/` | Thống kê real-time | Admin |

### AI (JSON API)

| Method | Endpoint | Mô tả | Quyền | Rate Limit |
|--------|----------|-------|-------|------------|
| POST | `/api/ai/summarize/<slug>/` | Tóm tắt tài liệu bằng AI | Login | 20/giờ |
| POST | `/api/ai/chat/<slug>/` | Chat hỏi đáp về tài liệu | Login | 60/giờ |
| POST | `/api/ai/suggest-tags/` | Gợi ý danh mục & tags | Login | — |
| POST | `/api/ai/general-chat/` | Chatbot tổng quát (EduBot) | Login | 60/giờ |

### Mã lỗi HTTP

| Code | Ý nghĩa | Xử lý |
|------|---------|-------|
| 200 | Thành công | — |
| 302 | Chuyển hướng | Redirect |
| 400 | Dữ liệu không hợp lệ | JSON `{"success": false, "error": "..."}` |
| 403 | Không có quyền | Trang 403 tùy chỉnh |
| 404 | Không tìm thấy | Trang 404 tùy chỉnh |
| 429 | Vượt rate limit | Trang 429 tùy chỉnh |
| 500 | Lỗi server | Trang 500 tùy chỉnh |

## 📝 Quy trình nghiệp vụ

### Quy trình đăng tải & duyệt tài liệu

```
Người dùng đăng tải → [Chờ duyệt] → Admin xem xét
                                        ├── Phê duyệt → [Đã duyệt] → Công khai
                                        └── Từ chối   → [Từ chối]  → Kèm lý do

* Nếu người dùng sửa tài liệu đã duyệt → Tự động chuyển về [Chờ duyệt]
* Mọi thay đổi trạng thái → Ghi nhật ký (SubmissionLog) + Gửi thông báo
```

### Luồng xử lý AI

```
Upload tài liệu (PDF/DOCX/TXT)
    → Trích xuất nội dung văn bản (PyPDF2/mammoth)
    → Gửi đến Groq API (LLaMA 3.3 70B)
    → Trả về: tóm tắt / câu trả lời / gợi ý tags
    → Cache kết quả trong session (giảm API calls)
```

## 🧪 Chạy Tests

```bash
python manage.py test                    # Tất cả
python manage.py test accounts           # Test app accounts
python manage.py test resources          # Test app resources
python manage.py test categories         # Test app categories
python manage.py test dashboard          # Test app dashboard
python manage.py test notifications      # Test app notifications
python manage.py test ai_features        # Test app ai_features
```

## 🔧 Cấu hình nâng cao

### Sử dụng ngrok (truy cập từ internet)

```bash
ngrok http 8000
```

Thêm domain ngrok vào `.env`:
```env
CSRF_TRUSTED_ORIGINS=https://your-subdomain.ngrok-free.app
```

### Biến môi trường (.env)

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `SECRET_KEY` | Django secret key | dev key |
| `DEBUG` | Chế độ debug | True |
| `DB_NAME` | Tên database (MySQL) | eduresource |
| `DB_USER` | Database user | root |
| `DB_PASSWORD` | Database password | (rỗng) |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 3306 |
| `GROQ_API_KEY` | Groq API key cho AI | (rỗng) |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins | (rỗng) |

## 📄 License

Dự án được phát triển cho mục đích học tập.

---

**EduResource** - Nền tảng chia sẻ tài liệu học tập © 2026
