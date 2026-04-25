# EduResource

Hệ thống chia sẻ tài liệu học tập trực tuyến xây dựng bằng Django.

## 1) Tổng quan

EduResource cho phép người dùng đăng tải, tìm kiếm, bình luận và đánh giá tài liệu học tập theo danh mục. Hệ thống có quy trình duyệt nội dung, dashboard quản trị, thông báo realtime (AJAX polling), và tính năng AI qua Groq.

### Tính năng chính
- Quản lý tài khoản: đăng ký/đăng nhập, hồ sơ cá nhân, đổi/quên/reset mật khẩu.
- Phân quyền theo vai trò: `guest`, `user`, `admin`.
- Quản lý tài liệu: tạo/sửa/xóa, upload file + thumbnail, preview/download.
- Tài liệu yêu thích: thêm/bỏ yêu thích và xem danh sách yêu thích cá nhân.
- Quy trình duyệt tài liệu: `pending` → `approved`/`rejected`.
- Bình luận + đánh giá sao cho tài liệu.
- Dashboard thống kê cho admin.
- Thông báo realtime và theo dõi người dùng online.
- AI features: tóm tắt tài liệu, chat theo tài liệu, gợi ý phân loại/tag, chatbot tổng quát.

## 2) Kiến trúc ứng dụng

Các app chính trong dự án:
- `accounts`: người dùng và phân quyền.
- `resources`: tài liệu, yêu thích, bình luận, nhật ký duyệt.
- `categories`: danh mục tài liệu.
- `dashboard`: thống kê và báo cáo.
- `notifications`: thông báo realtime + online users.
- `ai_features`: API AI dùng Groq.
- `eduresource`: cấu hình project (settings, urls, home, custom errors).

## 3) Công nghệ đang dùng

- Python 3.10+
- Django 4.2
- MySQL (mặc định) hoặc `DATABASE_URL`
- Whitenoise cho static files
- `django-ratelimit` cho giới hạn request
- Groq API (`llama-3.3-70b-versatile`) cho tính năng AI

## 4) Cài đặt local

### Bước 1: tạo môi trường ảo

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

### Bước 2: cài dependencies

```bash
pip install -r requirements.txt
```

> Lưu ý: code hiện tại import thêm `dj-database-url`, `whitenoise`, `groq`.
> Nếu thiếu, cài bổ sung:
>
> ```bash
> pip install dj-database-url whitenoise groq
> ```

### Bước 3: tạo file `.env`

Tạo `.env` ở thư mục gốc:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True

# Hosts
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=

# Database (chọn 1 trong 2 cách)
# Cách A: DATABASE_URL
# DATABASE_URL=mysql://user:password@localhost:3306/eduresource

# Cách B: MySQL params riêng
DB_NAME=eduresource
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_CONN_MAX_AGE=600

# AI
GROQ_API_KEY=

# Cache / static
CACHE_TIMEOUT=300
CACHE_MAX_ENTRIES=1000
WHITENOISE_MAX_AGE=0

# Security (local dev)
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
```

### Bước 4: migrate + seed

```bash
python manage.py migrate
python manage.py seed_data
```

### Bước 5: chạy server

```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000

## 5) Tài khoản mẫu (`seed_data`)

- Admin: `admin` / `admin123`
- User: `nguyenvana` / `user123`
- User: `tranthib` / `user123`
- User: `levanc` / `user123`
- User: `phamthid` / `user123`
- Guest: `khach` / `guest123`

## 6) API endpoints chính

### AI
- `POST /api/ai/summarize/<slug>/`
- `POST /api/ai/chat/<slug>/`
- `POST /api/ai/suggest-tags/`
- `POST /api/ai/general-chat/`

### Notifications / realtime
- `GET /api/notifications/`
- `POST /api/notifications/<pk>/read/`
- `POST /api/notifications/read-all/`
- `GET /api/search/`
- `GET /api/online-users/`
- `GET /api/dashboard-stats/`

### Resources
- `GET /resources/`
- `GET|POST /resources/create/`
- `GET /resources/favorites/`
- `GET /resources/<slug>/`
- `POST /resources/<slug>/favorite/`
- `POST /resources/<slug>/comment/`
- `GET /resources/<slug>/download/`
- `GET /resources/<slug>/preview/`

## 7) Cấu trúc thư mục (rút gọn)

```text
EduResources/
├── manage.py
├── requirements.txt
├── eduresource/
├── accounts/
├── categories/
├── resources/
├── dashboard/
├── notifications/
├── ai_features/
├── templates/
├── static/
└── media/
```

## 8) Lệnh hữu ích

```bash
# chạy test
python manage.py test

# tạo admin thủ công (nếu không dùng seed)
python manage.py createsuperuser

# collect static
python manage.py collectstatic --noinput
```

## 9) Ghi chú triển khai

- `DEBUG=False` trong production.
- Bật `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` khi chạy HTTPS.
- Thiết lập `ALLOWED_HOSTS` và `CSRF_TRUSTED_ORIGINS` đúng domain deploy.
- Nếu nền tảng deploy không có ổ đĩa persistent (ví dụ serverless), đặt `STORE_UPLOADS_IN_DB=True` để lưu nội dung PDF/Word trực tiếp trong DB (và app vẫn tải/preview bình thường khi file vật lý không còn).
- Sau khi thêm migration mới, chạy `python manage.py migrate`.
- Nếu muốn copy các file cũ từ `media/` vào DB, chạy `python manage.py backfill_file_blob --only-missing`.
- Cần `GROQ_API_KEY` để các API AI hoạt động.
- Tính năng yêu thích dùng bảng `resources_favorite`; migration tương ứng: `resources/migrations/0003_favorite_model.py`.

## 10) Deploy Railway (MySQL)

1. Tạo project mới trên Railway và kết nối repo GitHub.
2. Thêm service MySQL trong cùng project.
3. Gán biến môi trường cho service Django:
	- `SECRET_KEY=<your-secret>`
	- `DEBUG=False`
	- `DATABASE_URL=<mysql-url-from-railway>`
	- `ALLOWED_HOSTS=<your-app-domain>.up.railway.app`
	- `CSRF_TRUSTED_ORIGINS=https://<your-app-domain>.up.railway.app`
	- `STORE_UPLOADS_IN_DB=True`
	- `SESSION_COOKIE_SECURE=True`
	- `CSRF_COOKIE_SECURE=True`
	- `SECURE_SSL_REDIRECT=True`
4. Start command đề xuất:

```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn eduresource.wsgi:application --bind 0.0.0.0:$PORT
```

5. Với dữ liệu cũ đã upload từ local `media/`, chạy một lần để backfill vào DB:

```bash
python manage.py backfill_file_blob --only-missing
```
