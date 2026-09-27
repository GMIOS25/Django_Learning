# 🚀 BÁO CÁO & HƯỚNG DẪN DỰ ÁN DJANGO RESTFUL API
## Học phần: Phát triển Dịch vụ Web / RESTful API
> **Bài Thực Hành Số 1:** Cài đặt và cấu hình môi trường xây dựng API ("Hello World")  
> **Bài Thực Hành Số 2:** Router, Middleware và Bảo mật với JWT trong RESTful API  

---

## 📑 MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Yêu cầu đề bài & Bảng đối soát hoàn thành](#2-yêu-cầu-đề-bài--bảng-đối-soát-hoàn-thành)
3. [Kiến trúc hệ thống & Luồng xử lý (Workflow)](#3-kiến-trúc-hệ-thống--luồng-xử-lý-workflow)
4. [Cấu trúc cơ sở dữ liệu (Database Schema)](#4-cấu-trúc-cơ-sở-dữ-liệu-database-schema)
5. [Cấu trúc thư mục mã nguồn](#5-cấu-trúc-thư-mục-mã-nguồn)
6. [Yêu cầu môi trường & Công nghệ sử dụng](#6-yêu-cầu-môi-trường--công-nghệ-sử-dụng)
7. [Hướng dẫn cài đặt & Khởi chạy từ A-Z](#7-hướng-dẫn-cài-đặt--khởi-chạy-từ-a-z)
8. [Tài liệu API chi tiết (API Documentation)](#8-tài-liệu-api-chi-tiết-api-documentation)
9. [Hướng dẫn kiểm thử với Postman & Swagger UI](#9-hướng-dẫn-kiểm-thử-với-postman--swagger-ui)
10. [Kiểm thử tự động (Automated Unit Tests)](#10-kiểm-thử-tự-động-automated-unit-tests)
11. [Xử lý sự cố thường gặp (Troubleshooting)](#11-xử-lý-sự-cố-thường-gặp-troubleshooting)

---

## 1. TỔNG QUAN DỰ ÁN

Dự án này là chuỗi thực hành hoàn chỉnh nhằm xây dựng dịch vụ **RESTful API chuẩn hóa** sử dụng ngôn ngữ **Python** và nền tảng **Django / Django REST Framework (DRF)**.

Dự án tích hợp đầy đủ nội dung của 2 bài thực hành:
- **Bài thực hành số 1:** Thiết lập môi trường Python/Django, cài đặt REST Framework, xây dựng API đầu tiên in dòng chuỗi JSON `{"message": "hello-world"}` và kiểm thử qua Postman / Swagger.
- **Bài thực hành số 2:** Mở rộng hệ thống với:
  - Cơ chế định tuyến linh hoạt (**Router & URL Rewrite**).
  - Lớp lọc trung gian (**Custom Middleware**) để kiểm soát truy cập và xác thực token.
  - Cơ chế phân quyền và bảo mật qua **JSON Web Token (JWT)** với thuật toán HMAC-SHA256 (`HS256`).
  - Hỗ trợ giải mã mật khẩu truyền từ Client dưới dạng **Base64** hoặc mã băm **MD5**.
  - Tích hợp tài liệu tương tác tự động **Swagger UI (OpenAPI 3.0)**.

---

## 2. YÊU CẦU ĐỀ BÀI & BẢNG ĐỐI SOÁT HOÀN THÀNH

### Đối chiếu Bài Thực Hành Số 1:
- [x] Lựa chọn Framework: Python + Django REST Framework.
- [x] Cài đặt môi trường ảo `venv` sạch sẽ, cấu hình project `myapi` và app `core`.
- [x] Xây dựng API in chuỗi `{"message": "hello-world"}` kiểm thử được qua Postman / Swagger.

### Đối chiếu Bài Thực Hành Số 2:
| Yêu cầu trong PDF Bài 2 | Tình trạng | Vị trí triển khai trong Codebase |
| :--- | :---: | :--- |
| **1. Cài đặt thư viện JWT phù hợp** |  **100% Đạt** | Cài đặt `PyJWT 2.14.0`. Triển khai tại `core/utils.py` ([generate_jwt](file:///d:/CODES/Py/Django_Learning/core/utils.py#L9) & [decode_jwt](file:///d:/CODES/Py/Django_Learning/core/utils.py#L26)). |
| **2. Bảng User theo Phụ lục**<br>- `IdUser`: INT (PK)<br>- `UserName`: VARCHAR(255)<br>- `Password`: VARCHAR(255)<br>- `Token`: VARCHAR(255) |  **100% Đạt** | Model `User` tại `core/models.py`. Migration áp dụng tại `core/migrations/0001_initial.py`. Đã đăng ký hiển thị trong Django Admin tại `core/admin.py`. |
| **3. API Đăng nhập tại `localhost:****/`** |  **100% Đạt** | Định tuyến ngay tại gốc `http://localhost:8000/` và `http://localhost:8000/login` trong `myapi/urls.py` và `core/urls.py`. |
| **4. Tham số: userName, password (mã hóa Base64 hoặc MD5 từ client)** |  **100% Đạt** | `LoginSerializer` nhận `userName` (hoặc `username`). Hàm `verify_password` tại `core/utils.py` hỗ trợ giải mã Base64, so khớp băm MD5 và plain text. |
| **5. Kiểm tra tài khoản, sinh JWT & lưu vào cột Token** |  **100% Đạt** | Hàm `login_view` tại `core/views.py` sinh JWT hợp lệ và cập nhật trực tiếp vào thuộc tính `user.Token` trong database. |
| **6. API xác thực token `localhost:****/auth`** |  **100% Đạt** | Endpoint `/auth` tại `core/views.py` hỗ trợ nhận token qua Header `Authorization: Bearer <token>`, POST body `{"token": "..."}`, hoặc query string `?token=...`. |
| **7. Middleware bảo vệ API "Hello World" từ Bài 1** |  **100% Đạt** | `JWTAuthenticationMiddleware` tại `core/middleware.py`, đăng ký trong `settings.py`. Chặn `401 Unauthorized` nếu thiếu hoặc sai token; cho phép `200 OK` nếu token hợp lệ. |
| **8. Kiểm tra qua Postman / Swagger UI** |  **100% Đạt** | Tích hợp thư viện `drf-spectacular` tạo giao diện Swagger UI tại `http://localhost:8000/swagger/` và `http://localhost:8000/docs/`. |

---

## 3. KIẾN TRÚC HỆ THỐNG & LUỒNG XỬ LÝ (WORKFLOW)

### 3.1. Sơ đồ luồng xác thực và bảo vệ API
```text
+---------------------------------------------------------------------------------------+
|                                    CLIENT (Browser / Postman / Swagger)               |
+---------------------------------------------------------------------------------------+
       |                                                |
  (1) POST / (Login)                               (2) GET /hello (Có kèm Bearer Token)
  {userName, password (Base64/MD5)}                     |
       |                                                v
       v                                       +----------------------------------------+
+------------------------------------+         |       Django MIDDLEWARE Pipeline       |
|            ROUTER                  |         +----------------------------------------+
| (myapi/urls.py -> core/urls.py)    |                     |
+------------------------------------+                     v
       |                                       +----------------------------------------+
       v                                       |     JWTAuthenticationMiddleware        |
+------------------------------------+         +----------------------------------------+
|             VIEWS                  |                     |
|          login_view                |            [Kiểm tra Token hợp lệ?]
|  - Verify Password (Base64/MD5)    |                     |
|  - Generate JWT Token              |            +--------+--------+
|  - Save Token to User.Token        |            |                 |
+------------------------------------+         (KHÔNG)             (CÓ)
       |                                          |                 |
       v                                          v                 v
+------------------------------------+      +-----------+     +-------------------------+
|           DATABASE                 |      |  HTTP 401 |     |   Chuyển tiếp tới View  |
|    Bảng User (db.sqlite3)          |      |  Từ chối  |     |   hello_world -> 200 OK |
+------------------------------------+      +-----------+     +-------------------------+
```

### 3.2. Cơ chế xử lý mật khẩu Client (`verify_password`)
Nhằm đáp ứng linh hoạt các giao diện Client khác nhau, hệ thống hỗ trợ 3 định dạng mật khẩu:
1. **Base64 Encoding**: Ví dụ `123456` -> Base64: `MTIzNDU2`. Hệ thống tự động giải mã Base64 trước khi so sánh với mã băm trong DB.
2. **MD5 Hashing**: Ví dụ `123456` -> MD5: `e10adc3949ba59abbe56e057f20f883e`. Hệ thống so khớp trực tiếp chuỗi hash 32 ký tự.
3. **Plain Text**: Phục vụ việc kiểm thử nhanh qua cURL hoặc giao diện Swagger.

---

## 4. CẤU TRÚC CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)

Dự án sử dụng bảng dữ liệu **`User`** được cấu hình trong `core/models.py`:

```python
class User(models.Model):
    IdUser = models.AutoField(primary_key=True, db_column='IdUser')
    UserName = models.CharField(max_length=255, unique=True, db_column='UserName')
    Password = models.CharField(max_length=255, db_column='Password')
    Token = models.CharField(max_length=255, blank=True, null=True, db_column='Token')
```

### Bảng mô tả trường dữ liệu:

| Tên trường (Column) | Kiểu dữ liệu (Data Type) | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`IdUser`** | `INTEGER` (`AutoField`) | **PRIMARY KEY**, Auto Increment | Khóa chính định danh duy nhất cho người dùng |
| **`UserName`** | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` | Tên tài khoản hoặc email đăng nhập |
| **`Password`** | `VARCHAR(255)` | `NOT NULL` | Mật khẩu (được lưu trữ dưới dạng mã băm MD5 an toàn) |
| **`Token`** | `VARCHAR(255)` | `NULLABLE` | Lưu trữ chuỗi JWT mới nhất được cấp phát |

> 💡 **Tối ưu hóa độ dài chuỗi JWT:**  
> Chuỗi JWT tiêu chuẩn gồm 3 phần: `Header.Payload.Signature`. Để đảm bảo chuỗi JWT không bao giờ vượt quá giới hạn `VARCHAR(255)` của cột `Token`, payload trong `core/utils.py` được tối giản chỉ lưu các trường cốt lõi:
> `{"id": user.IdUser, "username": user.UserName, "exp": ..., "iat": ...}`.  
> Chiều dài chuỗi sinh ra luôn ổn định ở mức **~140 - 160 ký tự**, tránh triệt để lỗi tràn cột dữ liệu (Database Data Truncation).

---

## 5. CẤU TRÚC THƯ MỤC MÃ NGUỒN

```text
Django_Learning/
│
├── core/                               # Ứng dụng chính xử lý logic API
│   ├── management/
│   │   └── commands/
│   │       └── seed_user.py            # Lệnh tạo tài khoản mẫu kiểm thử nhanh
│   ├── migrations/
│   │   └── 0001_initial.py             # File khởi tạo lược đồ bảng User
│   ├── admin.py                        # Đăng ký quản trị bảng User trong Django Admin
│   ├── apps.py                         # Khai báo cấu hình ứng dụng Core
│   ├── middleware.py                   # JWTAuthenticationMiddleware lọc token cho /hello
│   ├── models.py                       # Model User (IdUser, UserName, Password, Token)
│   ├── serializers.py                  # Bộ tuần tự hóa dữ liệu cho Login, Auth, Register
│   ├── tests.py                        # Bộ 9 bài kiểm thử tự động toàn diện
│   ├── urls.py                         # Tuyến đường API cấp ứng dụng (/api/...)
│   ├── utils.py                        # Tiện ích: generate_jwt, decode_jwt, verify_password
│   └── views.py                        # Views: login_view, auth_view, hello_world, register_view
│
├── myapi/                              # Cấu hình dự án Django
│   ├── __init__.py
│   ├── asgi.py                         # Cấu hình ASGI Server
│   ├── settings.py                     # Khai báo INSTALLED_APPS, MIDDLEWARE, SPECTACULAR
│   ├── urls.py                         # Tuyến đường cấp hệ thống (Root routes & Swagger)
│   └── wsgi.py                         # Cấu hình WSGI Server
│
├── docs/                               # Thư mục chứa đề bài thực hành
│   ├── BÀI THỰC HÀNH SỐ 1.pdf          # Đề bài 1: Cài đặt môi trường & Hello World API
│   └── BÀI THỰC HÀNH SỐ 2.pdf          # Đề bài 2: Router, Middleware & JWT
│
├── db.sqlite3                          # Cơ sở dữ liệu SQLite cục bộ
├── manage.py                           # Tập lệnh quản trị Django CLI
├── requirements.txt                    # Danh sách các gói thư viện phụ thuộc
├── tutorial.md                         # Ghi chú hướng dẫn bài thực hành số 1
└── README.md                           # Báo cáo và tài liệu hướng dẫn toàn diện
```

---

## 6. YÊU CẦU MÔI TRƯỜNG & CÔNG NGHỆ SỬ DỤNG

### Công nghệ nền tảng:
- **Python:** Phiên bản `>= 3.10`
- **Django:** Phiên bản `6.1.1` (hoặc các phiên bản `5.x / 6.x`)
- **Django REST Framework (DRF):** `3.18.1`
- **PyJWT:** `2.14.0` (Thư viện xử lý JWT)
- **drf-spectacular:** `0.30.0` (Bộ sinh tài liệu OpenAPI 3.0 & Swagger UI)
- **SQLite3:** Hệ quản trị cơ sở dữ liệu nhúng

---

## 7. HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY TỪ A-Z

### Bước 1: Mở Terminal và Kích hoạt Môi trường ảo (Virtualenv)

Di chuyển vào thư mục dự án `Django_Learning`:

- **Trên Windows (PowerShell):**
  ```powershell
  # Nếu bị chặn bởi chính sách ExecutionPolicy, chạy lệnh sau trước:
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

  # Kích hoạt venv
  .\venv\Scripts\Activate.ps1
  ```
- **Trên Windows (Command Prompt - CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Trên macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
*(Khi kích hoạt thành công, đầu dòng lệnh terminal sẽ xuất hiện tiền tố `(venv)`)*

---

### Bước 2: Cài đặt thư viện phụ thuộc
Nếu bạn clone mã nguồn sang máy mới chưa có sẵn thư mục `venv`, thực hiện:
```bash
python -m venv venv
pip install -r requirements.txt
```

---

### Bước 3: Đồng bộ Cơ sở dữ liệu (Migration)
Khởi tạo và cập nhật cấu trúc bảng `User` vào file `db.sqlite3`:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Bước 4: Tạo tài khoản mẫu để kiểm thử (Seed Data)
Dự án đã tích hợp sẵn lệnh tạo nhanh tài khoản mẫu:
```bash
python manage.py seed_user
```
**Thông tin tài khoản mẫu được tạo sẵn:**
- **Tài khoản (`userName`):** `testuser`
- **Mật khẩu gốc (Plain text):** `123456`
- **Mật khẩu Base64:** `MTIzNDU2`
- **Mật khẩu băm MD5:** `e10adc3949ba59abbe56e057f20f883e`

*(Tùy chọn: Nếu muốn truy cập trang quản trị `/admin/`, tạo tài khoản Superuser bằng lệnh: `python manage.py createsuperuser`)*

---

### Bước 5: Khởi động máy chủ phát triển (Development Server)
```bash
python manage.py runserver
```
Máy chủ sẽ lắng nghe tại địa chỉ: `http://127.0.0.1:8000/` (hoặc `http://localhost:8000/`)

---

## 8. TÀI LIỆU API CHI TIẾT (API DOCUMENTATION)

### Danh sách Endpoint tổng quan:

| Nhóm chức năng | Phương thức | Đường dẫn (URL) | Mô tả tóm tắt | Quyền truy cập |
| :--- | :---: | :--- | :--- | :---: |
| **Login** | `POST` | `/` hoặc `/login` | Đăng nhập và cấp phát chuỗi JWT | Public |
| **Auth** | `GET` / `POST` | `/auth` | Xác thực tính hợp lệ của Token | Public |
| **Hello World** | `GET` | `/hello` hoặc `/api/hello/` | API Bài 1 in dòng `hello-world` |  **Cần Bearer Token** |
| **Register** | `POST` | `/register` | Đăng ký tài khoản người dùng mới | Public |
| **Swagger UI** | `GET` | `/swagger/` hoặc `/docs/` | Giao diện tài liệu API trực quan | Public |
| **OpenAPI Schema** | `GET` | `/api/schema/` | Tải về cấu hình JSON/YAML OpenAPI | Public |
| **Django Admin** | `GET` | `/admin/` | Trang quản trị dữ liệu hệ thống | Cần tài khoản Admin |

---

### Chi tiết từng Endpoint

#### 8.1. API Đăng nhập (Sinh JWT Token)
- **Phương thức:** `POST`
- **Đường dẫn:** `http://localhost:8000/` hoặc `http://localhost:8000/login`
- **Headers:** `Content-Type: application/json`
- **Body JSON (Hỗ trợ Base64 hoặc MD5):**
  - *Ví dụ 1: Gửi mật khẩu dạng Base64 (`123456` -> `MTIzNDU2`):*
    ```json
    {
      "userName": "testuser",
      "password": "MTIzNDU2"
    }
    ```
  - *Ví dụ 2: Gửi mật khẩu dạng mã băm MD5:*
    ```json
    {
      "userName": "testuser",
      "password": "e10adc3949ba59abbe56e057f20f883e"
    }
    ```
- **Phản hồi thành công (`200 OK`):**
  ```json
  {
    "message": "Đăng nhập thành công",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsImV4cCI6MTc4OTk2MzkxOSwiaWF0IjoxNzg5OTU2NzE5fQ.xxx...",
    "user": {
      "IdUser": 1,
      "UserName": "testuser"
    }
  }
  ```
- **Phản hồi khi sai tài khoản/mật khẩu (`401 Unauthorized`):**
  ```json
  {
    "error": "Unauthorized",
    "detail": "Mật khẩu không chính xác."
  }
  ```
- **Lệnh cURL kiểm thử nhanh:**
  ```bash
  curl -X POST http://localhost:8000/ \
    -H "Content-Type: application/json" \
    -d "{\"userName\": \"testuser\", \"password\": \"MTIzNDU2\"}"
  ```

---

#### 8.2. API Xác thực Token (Auth)
- **Phương thức:** `GET` hoặc `POST`
- **Đường dẫn:** `http://localhost:8000/auth`
- **Cách truyền Token (chọn 1 trong 3 cách):**
  - **Cách 1 (Khuyên dùng):** Qua Header `Authorization: Bearer <chuỗi_token>`
  - **Cách 2:** Qua Body `{"token": "<chuỗi_token>"}` (Phương thức `POST`)
  - **Cách 3:** Qua Query param: `http://localhost:8000/auth?token=<chuỗi_token>`
- **Phản hồi khi Token hợp lệ (`200 OK`):**
  ```json
  {
    "valid": true,
    "message": "Token hợp lệ và còn hiệu lực.",
    "payload": {
      "id": 1,
      "username": "testuser",
      "exp": 1789963919,
      "iat": 1789956719
    },
    "user": {
      "IdUser": 1,
      "UserName": "testuser",
      "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  }
  ```
- **Phản hồi khi Token hết hạn hoặc sai chữ ký (`401 Unauthorized`):**
  ```json
  {
    "valid": false,
    "error": "Invalid Token",
    "detail": "Chữ ký Token không hợp lệ (Invalid Signature)."
  }
  ```
- **Lệnh cURL kiểm thử nhanh:**
  ```bash
  curl -X GET http://localhost:8000/auth \
    -H "Authorization: Bearer <DÁN_CHUỖI_TOKEN_VÀO_ĐÂY>"
  ```

---

#### 8.3. API "Hello World" (Được bảo vệ bởi Middleware)
- **Phương thức:** `GET`
- **Đường dẫn:** `http://localhost:8000/hello` hoặc `http://localhost:8000/api/hello/`
- **Yêu cầu:** Bắt buộc phải đính kèm Header `Authorization: Bearer <chuỗi_token>`
- **Trường hợp 1: Không có Header Authorization hoặc Token sai (`401 Unauthorized` do Middleware chặn):**
  ```json
  {
    "error": "Unauthorized",
    "detail": "Vui lòng cung cấp JWT token qua Header 'Authorization: Bearer <token>' để truy cập API này."
  }
  ```
- **Trường hợp 2: Có Token hợp lệ (`200 OK` do Middleware phê duyệt):**
  ```json
  {
    "message": "hello-world",
    "authenticated_user": {
      "IdUser": 1,
      "UserName": "testuser"
    }
  }
  ```
- **Lệnh cURL kiểm thử:**
  ```bash
  # Thử nghiệm 1: Gọi không có token -> Sẽ nhận lỗi 401
  curl -i http://localhost:8000/hello

  # Thử nghiệm 2: Gọi kèm Bearer token -> Nhận kết quả hello-world 200 OK
  curl -X GET http://localhost:8000/hello \
    -H "Authorization: Bearer <DÁN_CHUỖI_TOKEN_VÀO_ĐÂY>"
  ```

---

#### 8.4. API Đăng ký tài khoản mới (Register)
- **Phương thức:** `POST`
- **Đường dẫn:** `http://localhost:8000/register`
- **Body JSON:**
  ```json
  {
    "userName": "sinhvien_cntt",
    "password": "Password@2026"
  }
  ```
- **Phản hồi thành công (`201 Created`):**
  ```json
  {
    "message": "Tạo tài khoản thành công!",
    "user": {
      "IdUser": 2,
      "UserName": "sinhvien_cntt"
    }
  }
  ```

---

## 9. HƯỚNG DẪN KIỂM THỬ VỚI POSTMAN & SWAGGER UI

### 9.1. Kiểm thử trực quan trên Swagger UI
1. Mở trình duyệt web và truy cập: **`http://localhost:8000/swagger/`**
2. Tìm đến mục **`POST /` (Dịch vụ Đăng nhập)**:
   - Nhấn **Try it out**.
   - Nhập thông tin đăng nhập: `userName: testuser`, `password: MTIzNDU2`.
   - Bấm **Execute**.
   - Copy toàn bộ chuỗi token nằm trong trường `"token": "..."` ở phần kết quả trả về.
3. Kéo lên đầu trang Swagger, nhấn vào nút **Authorize 🔓** (có biểu tượng ổ khóa màu xanh lá cây):
   - Nhập vào ô Value: chuỗi token vừa copy (Swagger tự động hỗ trợ định dạng Bearer).
   - Nhấn **Authorize** rồi nhấn **Close**.
4. Tìm đến mục **`GET /hello` (API Hello World)**:
   - Nhấn **Try it out** -> **Execute**.
   - Quan sát kết quả: Hệ thống trả về `200 OK` cùng chuỗi `{"message": "hello-world"}`.
   - Thử nhấn **Logout** ở nút Authorize rồi gọi lại `/hello` để thấy Middleware chặn lại với mã lỗi `401 Unauthorized`.

---

### 9.2. Kiểm thử trên Postman
1. **Request 1 - Đăng nhập:**
   - Method: `POST` | URL: `http://localhost:8000/login`
   - Body -> chọn `raw` -> `JSON`:
     ```json
     {
       "userName": "testuser",
       "password": "MTIzNDU2"
     }
     ```
   - Gửi request và sao chép chuỗi `token`.
2. **Request 2 - Xác thực Token:**
   - Method: `GET` | URL: `http://localhost:8000/auth`
   - Headers: Thêm Key `Authorization`, Value: `Bearer <chuỗi_token>`.
3. **Request 3 - Gọi API Hello World:**
   - Method: `GET` | URL: `http://localhost:8000/hello`
   - Tab **Authorization**: Chọn Type là `Bearer Token`, dán mã token vào ô Token.
   - Nhấn **Send** -> Kết quả hiển thị `"message": "hello-world"`.

---

## 10. KIỂM THỬ TỰ ĐỘNG (AUTOMATED UNIT TESTS)

Dự án được xây dựng kèm bộ test tự động độc lập tại file [core/tests.py](file:///d:/CODES/Py/Django_Learning/core/tests.py) sử dụng `APITestCase` của Django REST Framework.

### Lệnh chạy toàn bộ test:
```powershell
python manage.py test
```

### Kết quả chạy kiểm thử thực tế:
```text
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.........
----------------------------------------------------------------------
Ran 9 tests in 2.400s

OK
Destroying test database for alias 'default'...
```

### Chi tiết 9 trường hợp kiểm thử (Test Cases):
1. `test_01_login_with_base64_password`: Xác minh đăng nhập thành công với mật khẩu mã hóa Base64 và kiểm tra việc lưu chuỗi token vào cột `Token` trong database.
2. `test_02_login_with_md5_password`: Xác minh đăng nhập thành công khi client gửi mật khẩu dạng băm MD5.
3. `test_03_login_with_plain_password`: Xác minh đăng nhập bằng mật khẩu văn bản thô.
4. `test_04_login_wrong_password`: Xác minh hệ thống từ chối và trả về mã lỗi `401 Unauthorized` khi nhập sai mật khẩu.
5. `test_05_auth_token_endpoint`: Kiểm tra API `/auth` giải mã và xác nhận tính hợp lệ của token qua cả Header Authorization và POST body.
6. `test_06_middleware_blocks_hello_world_without_token`: Kiểm tra Middleware chặn request truy cập `/hello` khi không có token (trả về mã 401).
7. `test_07_middleware_blocks_hello_world_with_invalid_token`: Kiểm tra Middleware chặn request truy cập `/hello` khi token giả mạo hoặc sai định dạng.
8. `test_08_middleware_allows_hello_world_with_valid_token`: Kiểm tra Middleware cho phép truy cập `/hello` khi cung cấp token JWT hợp lệ.
9. `test_09_register_endpoint`: Kiểm tra quy trình đăng ký tài khoản mới và lưu mật khẩu dạng băm an toàn vào cơ sở dữ liệu.

---

## 11. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

### 1. Lỗi PowerShell không cho kích hoạt `venv` (`running scripts is disabled on this system`)
- **Nguyên nhân:** Chính sách bảo mật ExecutionPolicy của Windows hạn chế chạy script `.ps1`.
- **Cách khắc phục:** Mở PowerShell và chạy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  .\venv\Scripts\Activate.ps1
  ```

### 2. Gọi `/hello` luôn nhận thông báo lỗi 401 Unauthorized
- **Nguyên nhân:** Bạn chưa truyền Header `Authorization` hoặc chưa thêm tiền tố `Bearer ` trước chuỗi token.
- **Cách khắc phục:** Đảm bảo Header có định dạng chính xác:
  ```text
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
  ```
  *(Chú ý có dấu cách giữa từ `Bearer` và chuỗi token)*.

### 3. Cổng 8000 bị xung đột hoặc đang được tiến trình khác sử dụng
- **Cách khắc phục:** Khởi chạy máy chủ trên cổng khác (ví dụ cổng 8080):
  ```powershell
  python manage.py runserver 8080
  ```
  Khi đó đường dẫn API sẽ là `http://localhost:8080/`.

---

## 👨‍💻 THÔNG TIN DỰ ÁN & TÁC GIẢ

- **Đơn vị đào tạo:** Bộ môn Mạng máy tính & Truyền thông / Kỹ thuật Phần mềm
- **Môn học:** Phát triển Ứng dụng Phân tán & Web Services (RESTful API)
- **Tài liệu tham chiếu:** [BÀI THỰC HÀNH SỐ 1.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%201.pdf) và [BÀI THỰC HÀNH SỐ 2.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%202.pdf)
