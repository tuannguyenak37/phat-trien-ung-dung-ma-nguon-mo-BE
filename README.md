<div align="center">

# 🛠️ ĐỀ TÀI 11: COMMUNITY FORUM (BACKEND API)
### (Hệ thống API cho Diễn đàn thảo luận trực tuyến)

**Môn học:** Phát triển ứng dụng mã nguồn mở  
**Giảng viên hướng dẫn:** GV. Lê Duy Hùng

---
</div>

## 👥 Thành Viên Nhóm

| STT | Họ và Tên | Mã Sinh Viên | Vai Trò | GitHub |
|:---:|:---|:---:|:---|:---:|
| 1 | **Nguyễn Văn Tuấn** | 23050150 | Trưởng nhóm / Backend  |
| 2 | **Nguyễn Thị Vân Khánh** | 23050183 | | 

---

## 📖 1. Tổng Quan Hệ Thống

Đây là **Backend Server** phục vụ cho hệ thống Community Forum. Server cung cấp các RESTful API hiệu suất cao, đảm nhận việc xử lý logic nghiệp vụ, xác thực người dùng và tương tác với cơ sở dữ liệu.

### 🌟 Tính năng API chính
* 🔐 **Authentication:** JWT (JSON Web Tokens) cho Đăng ký, Đăng nhập, Refresh Token.
* 👤 **User Management:** Quản lý profile, avatar, phân quyền (Admin/User).
* 📝 **Post System:** CRUD bài viết, hỗ trợ Markdown content.
* 💬 **Interaction:** API bình luận, like/unlike bài viết.
* 🔍 **Search & Filter:** API tìm kiếm bài viết theo từ khóa và danh mục.
* 📄 **Documentation:** Tự động tạo document chuẩn OpenAPI (Swagger UI).

---

## 🛠 2. Công Nghệ Sử Dụng

| Thành phần | Công nghệ / Thư viện |
| :--- | :--- |
| **Ngôn ngữ** | Python 3.10+ |
| **Framework** | FastAPI |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 
| **Validation** | Pydantic |
| **Migration** | Alembic |
| **Server** | Uvicorn |
| **Deployment** | Render Web Service |

---

## 🚀 3. Hướng Dẫn Cài Đặt (Local Development)

### Bước 1: Clone dự án
```bash
git clone [https://github.com/username/community-forum-be.git](https://github.com/username/community-forum-be.git)
cd community-forum-be
Bước 2: Tạo môi trường ảo (Virtual Environment)
Bash

python -m venv venv
# Kích hoạt môi trường:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
Bước 3: Cài đặt thư viện
Bash

pip install -r requirements.txt
Bước 4: Cấu hình biến môi trường (.env)
Tạo file .env tại thư mục gốc và cấu hình kết nối PostgreSQL local:

Đoạn mã

DATABASE_URL="postgresql://user:password@localhost:5432/community_db"
SECRET_KEY="your_super_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
Bước 5: Chạy Server
Bash

uvicorn main:app --reload
API chạy tại: http://127.0.0.1:8000

Swagger Docs tại: http://127.0.0.1:8000/docs

☁️ 4. Hướng Dẫn Triển Khai (Deploy) trên Render
Render là nền tảng đám mây lý tưởng để deploy FastAPI và PostgreSQL.

Giai đoạn 1: Tạo Database trên Render
Đăng nhập Render Dashboard.

Chọn New + ➡️ PostgreSQL.

Điền tên Database (VD: forum-db), các thông số khác để mặc định.

Sau khi tạo xong, copy Internal Database URL (dùng cho deploy cùng mạng Render) hoặc External Database URL (để test từ máy local).

Giai đoạn 2: Deploy FastAPI Web Service
Tại Dashboard, chọn New + ➡️ Web Service.

Kết nối với GitHub Repository của nhóm.

Cấu hình các thông số sau:

Name: community-forum-api (hoặc tên tùy thích).

Runtime: Python 3.

Build Command: pip install -r requirements.txt (Nếu có file build.sh thì dùng ./build.sh).

Start Command:

Bash

uvicorn main:app --host 0.0.0.0 --port $PORT
(Lưu ý: thay main:app bằng tên_file_chính:app của bạn).

Environment Variables (Biến môi trường): Nhấn vào Advanced ➡️ Add Environment Variable:

PYTHON_VERSION: 3.10.0 (Khuyến nghị).

DATABASE_URL: Paste link Internal Database URL vừa copy ở Giai đoạn 1 (Lưu ý: Nếu dùng SQLAlchemy, hãy sửa postgres:// thành postgresql:// trong chuỗi kết nối).

SECRET_KEY: Điền secret key của bạn.

Nhấn Create Web Service.

Giai đoạn 3: Hoàn tất
Chờ Render build và deploy (khoảng 2-3 phút).

Khi trạng thái báo Live, truy cập link API (ví dụ: https://community-forum.onrender.com/docs) để kiểm tra Swagger UI.

📂 Cấu trúc thư mục (Tham khảo)
Plaintext

├── app/
│   ├── routers/       # Các file định nghĩa API route
│   ├── models/        # Database models (SQLAlchemy)
│   ├── schemas/       # Pydantic schemas (Request/Response)
│   ├── core/          # Config, Security, Database connection
│   └── main.py        # Entry point của ứng dụng
├── alembic/           # Database migrations
├── .env               # Biến môi trường (không push lên git)
├── .gitignore
├── requirements.txt   # Danh sách thư viện
└── README.md
© 2025 - Nhóm 11: Community Forum