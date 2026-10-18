# 🚀 BÁO CÁO & HƯỚNG DẪN DỰ ÁN DJANGO RESTFUL API
## Học phần: Phát triển Dịch vụ Web / RESTful API
> **Bài Thực Hành Số 1:** Cài đặt và cấu hình môi trường xây dựng API ("Hello World")  
> **Bài Thực Hành Số 2:** Router, Middleware và Bảo mật với JWT trong RESTful API  
> **Bài Thực Hành Số 3:** Xây dựng Dịch vụ Quản lý Sản phẩm theo Kiến trúc Hướng Dịch vụ (SOA)  

---

## 📑 MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Yêu cầu đề bài & Bảng đối soát hoàn thành](#2-yêu-cầu-đề-bài--bảng-đối-soát-hoàn-thành)
3. [Kiến trúc hệ thống & Luồng xử lý (Workflow SOA)](#3-kiến-trúc-hệ-thống--luồng-xử-lý-workflow)
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

Dự án này là chuỗi thực hành hoàn chỉnh nhằm xây dựng hệ thống **RESTful API phân tán theo kiến trúc hướng dịch vụ (SOA - Service-Oriented Architecture)** sử dụng ngôn ngữ **Python** và nền tảng **Django / Django REST Framework (DRF)**.

Dự án tích hợp đầy đủ nội dung của **cả 3 bài thực hành**:
- **Bài thực hành số 1:** Thiết lập môi trường Python/Django, cài đặt REST Framework, xây dựng API đầu tiên in dòng chuỗi JSON `{"message": "hello-world"}` và kiểm thử qua Postman / Swagger.
- **Bài thực hành số 2:** Mở rộng hệ thống thành **Authentication Service (Cổng 8000)**:
  - Cơ chế định tuyến linh hoạt (**Router & URL Rewrite**).
  - Lớp lọc trung gian (**Custom Middleware**) để kiểm soát truy cập và xác thực token.
  - Cơ chế phân quyền và bảo mật qua **JSON Web Token (JWT)** với thuật toán HMAC-SHA256 (`HS256`).
  - Hỗ trợ giải mã mật khẩu truyền từ Client dưới dạng **Base64** hoặc mã băm **MD5**.
  - Tích hợp tài liệu tương tác tự động **Swagger UI (OpenAPI 3.0)**.
- **Bài thực hành số 3:** Xây dựng **Product Management Service (Cổng 8001)** độc lập theo kiến trúc **SOA**:
  - Chạy trên một cổng riêng (`localhost:8001/`) và cơ sở dữ liệu SQLite riêng (`products_db.sqlite3`).
  - Đầy đủ bộ RESTful API CRUD: `GET /products`, `GET /products/:id`, `POST /products`, `PUT /products/:id`, `PATCH /products/:id`, `DELETE /products/:id`.
  - Cơ chế xác thực liên dịch vụ (**Inter-Service Authentication**): Product Service tự động liên lạc sang Auth Service (`http://127.0.0.1:8000/auth`) để thẩm định tính hợp lệ của token JWT.
  - Tích hợp tài liệu Swagger UI riêng biệt tại `http://localhost:8001/swagger/`.

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

### Đối chiếu Bài Thực Hành Số 3:
| Yêu cầu trong PDF Bài 3 | Tình trạng | Vị trí triển khai trong Codebase |
| :--- | :---: | :--- |
| **1. Khởi tạo một cổng mới cho service (`localhost:***1/`)** |  **100% Đạt** | Service quản lý sản phẩm chạy độc lập trên cổng `8001` (`http://localhost:8001/`). Có script chạy riêng [run_product_service.bat](file:///d:/CODES/Py/Django_Learning/run_product_service.bat). |
| **2. Cơ sở dữ liệu riêng biệt theo nguyên tắc SOA** |  **100% Đạt** | Tách cơ sở dữ liệu riêng `product_service/products_db.sqlite3` không dùng chung bảng hay file SQLite với Auth Service. |
| **3. Bảng sản phẩm (`products`) theo Phụ lục**<br>- `id`: INT (PK)<br>- `name`: VARCHAR(255)<br>- `description`: TEXT<br>- `price`: DECIMAL(10, 2)<br>- `quantity`: INT<br>- `created_at`: TIMESTAMP<br>- `updated_at`: TIMESTAMP |  **100% Đạt** | Model `Product` tại [product_service/products/models.py](file:///d:/CODES/Py/Django_Learning/product_service/products/models.py). Đã tạo migration và đăng ký trong Django Admin [product_service/products/admin.py](file:///d:/CODES/Py/Django_Learning/product_service/products/admin.py). |
| **4. RESTful API `GET /products`** |  **100% Đạt** | Lấy toàn bộ danh sách sản phẩm (hỗ trợ lọc `?search=...`). Triển khai tại `products/views.py`. |
| **5. RESTful API `GET /products/:id`** |  **100% Đạt** | Lấy chi tiết thông tin một sản phẩm (trả về 404 nếu không tìm thấy). |
| **6. RESTful API `POST /products`** |  **100% Đạt** | Thêm sản phẩm mới, kiểm tra tính hợp lệ dữ liệu (giá >= 0, số lượng >= 0, tên không rỗng), trả về `201 Created`. |
| **7. RESTful API `PUT /products/:id`** |  **100% Đạt** | Cập nhật thông tin sản phẩm (hỗ trợ cả `PATCH` cho cập nhật từng phần), tự động cập nhật `updated_at`. |
| **8. RESTful API `DELETE /products/:id`** |  **100% Đạt** | Xóa sản phẩm khỏi database, trả về phản hồi xác nhận xóa thành công. |
| **9. Xác thực qua service ở Bài thực hành số 2** |  **100% Đạt** | Lớp xác thực [AuthServiceAuthentication](file:///d:/CODES/Py/Django_Learning/product_service/products/authentication.py) tự động gửi request HTTP sang `http://127.0.0.1:8000/auth` để xác thực token JWT, chặn 401 nếu token không hợp lệ hoặc đã hết hạn. |
| **10. Swagger UI & Kiểm thử tự động** |  **100% Đạt** | Swagger UI tương tác tại `http://localhost:8001/swagger/`. Bộ 17 bài Unit & Integration Tests đạt 100% tại `product_service/products/tests.py`. |

---

## 3. KIẾN TRÚC HỆ THỐNG & LUỒNG XỬ LÝ (WORKFLOW SOA)

### 3.1. Sơ đồ kiến trúc SOA (Kiến trúc hướng dịch vụ 2 Services độc lập)
```text
+---------------------------------------------------------------------------------------------------+
|                                 CLIENT (Postman / Browser / Swagger UI)                           |
+---------------------------------------------------------------------------------------------------+
             |                                                                 |
    (1) Đăng nhập lấy JWT Token                                       (3) Thao tác CRUD Sản phẩm
    POST http://localhost:8000/login                                  GET/POST/PUT/DELETE http://localhost:8001/products
             |                                                                 | (Kèm Header Authorization: Bearer <token>)
             v                                                                 v
+-------------------------------------------+               +-------------------------------------------+
|          DỊCH VỤ 1: AUTH SERVICE          |               |        DỊCH VỤ 2: PRODUCT SERVICE         |
|         (Chạy tại cổng :8000)             |               |           (Chạy tại cổng :8001)           |
|                                           |  (4) HTTP     |                                           |
|  - Cấp phát JWT & mã hóa MD5/Base64       |<--------------|  - Controller CRUD Sản phẩm               |
|  - Middleware bảo vệ /hello               |    POST /auth |  - AuthServiceAuthentication              |
|  - Endpoint xác thực token: /auth         |    (Xác thực  |  - Giao diện Swagger: :8001/swagger/      |
|  - Swagger UI: :8000/swagger/             |     liên SV)  |                                           |
+-------------------------------------------+               +-------------------------------------------+
                     |                                                                 |
                     v                                                                 v
+-------------------------------------------+               +-------------------------------------------+
|          DATABASE RIÊNG: db.sqlite3       |               |     DATABASE RIÊNG: products_db.sqlite3   |
|                 (Bảng User)               |               |              (Bảng products)              |
+-------------------------------------------+               +-------------------------------------------+
```

### 3.2. Luồng xác thực liên dịch vụ (Inter-Service Authentication)
1. **Bước 1 (Client -> Auth Service):** Client gửi `POST http://localhost:8000/login` với `userName` và `password` (Base64 hoặc MD5). Auth Service trả về chuỗi `token` JWT.
2. **Bước 2 (Client -> Product Service):** Client gọi API quản lý sản phẩm `http://localhost:8001/products` kèm Header `Authorization: Bearer <token>`.
3. **Bước 3 (Product Service -> Auth Service):** Lớp `AuthServiceAuthentication` của Product Service tự động gửi request HTTP `POST http://127.0.0.1:8000/auth` để hỏi Auth Service tính hợp lệ của token.
4. **Bước 4 (Phản hồi & Thực thi):**
   - Nếu Auth Service trả về `valid: true`: Product Service thực hiện truy vấn cơ sở dữ liệu `products_db.sqlite3` và trả về kết quả (200 OK / 201 Created).
   - Nếu Token sai, hết hạn hoặc Auth Service trả về 401: Product Service lập tức từ chối với mã lỗi `401 Unauthorized`.

---

## 4. CẤU TRÚC CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)

Tuân thủ nguyên tắc kiến trúc SOA, mỗi dịch vụ sở hữu cơ sở dữ liệu hoàn toàn tách biệt:

### 4.1. Bảng `User` (Auth Service - file `db.sqlite3`)

```python
class User(models.Model):
    IdUser = models.AutoField(primary_key=True, db_column='IdUser')
    UserName = models.CharField(max_length=255, unique=True, db_column='UserName')
    Password = models.CharField(max_length=255, db_column='Password')
    Token = models.CharField(max_length=255, blank=True, null=True, db_column='Token')
```

| Tên trường (Column) | Kiểu dữ liệu | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`IdUser`** | `INTEGER` (`AutoField`) | **PRIMARY KEY**, Auto Increment | Khóa chính định danh duy nhất cho người dùng |
| **`UserName`** | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` | Tên tài khoản hoặc email đăng nhập |
| **`Password`** | `VARCHAR(255)` | `NOT NULL` | Mật khẩu (lưu dạng băm MD5) |
| **`Token`** | `VARCHAR(255)` | `NULLABLE` | Lưu trữ chuỗi JWT mới nhất được cấp phát |

### 4.2. Bảng `products` (Product Service - file `product_service/products_db.sqlite3`)

```python
class Product(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(max_length=255, db_column='name')
    description = models.TextField(blank=True, null=True, db_column='description')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='price')
    quantity = models.IntegerField(default=0, db_column='quantity')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')
```

| Tên trường (Column) | Kiểu dữ liệu | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`id`** | `INT` (`AutoField`) | **PRIMARY KEY**, Auto Increment | ID duy nhất của sản phẩm |
| **`name`** | `VARCHAR(255)` | `NOT NULL` | Tên sản phẩm |
| **`description`** | `TEXT` | `NULLABLE` | Mô tả chi tiết về sản phẩm |
| **`price`** | `DECIMAL(10, 2)` | `NOT NULL`, `>= 0` | Giá bán của sản phẩm |
| **`quantity`** | `INT` | `DEFAULT 0`, `>= 0` | Số lượng sản phẩm còn lại trong kho |
| **`created_at`** | `TIMESTAMP` | `auto_now_add=True` | Ngày giờ sản phẩm được tạo |
| **`updated_at`** | `TIMESTAMP` | `auto_now=True` | Ngày giờ sản phẩm được cập nhật gần nhất |

---

## 5. CẤU TRÚC THƯ MỤC MÃ NGUỒN

```text
Django_Learning/
│
├── core/                               # SERVICE 1: Ứng dụng Auth (Bài 1 & 2)
│   ├── management/commands/seed_user.py # Lệnh tạo tài khoản mẫu 'testuser'
│   ├── migrations/0001_initial.py      # Schema bảng User
│   ├── admin.py                        # Quản trị User trong Django Admin
│   ├── middleware.py                   # JWTAuthenticationMiddleware chặn /hello
│   ├── models.py                       # Model User
│   ├── serializers.py                  # Serializer Login, Auth, Register
│   ├── tests.py                        # 9 bài kiểm thử tự động cho Service 1
│   ├── urls.py                         # Route cấp ứng dụng (/api/...)
│   ├── utils.py                        # JWT encode/decode, verify_password
│   └── views.py                        # Views login, auth, hello_world, register
│
├── myapi/                              # Cấu hình dự án Service 1 (Port 8000)
│   ├── settings.py                     # DB: db.sqlite3, JWT, Swagger :8000
│   └── urls.py                         # Root routes & Swagger UI :8000
│
├── product_service/                    # SERVICE 2: Quản lý Sản phẩm (Bài 3 - SOA)
│   ├── manage.py                       # CLI riêng cho Product Service (Port 8001)
│   ├── products_db.sqlite3             # Database SQLite riêng biệt của Product Service
│   ├── product_project/                # Cấu hình dự án Service 2
│   │   ├── settings.py                 # DB riêng, AUTH_SERVICE_URL, Swagger :8001
│   │   ├── urls.py                     # Định tuyến /products, /swagger :8001
│   │   ├── asgi.py & wsgi.py
│   └── products/                       # Ứng dụng Sản phẩm
│       ├── management/commands/seed_products.py # Lệnh tạo danh sách sản phẩm mẫu
│       ├── migrations/0001_initial.py  # Schema bảng products
│       ├── admin.py                    # Quản trị Product trong Django Admin :8001
│       ├── authentication.py           # Xác thực liên dịch vụ sang Service 1 (:8000/auth)
│       ├── models.py                   # Model Product theo Phụ lục Bài 3
│       ├── serializers.py              # Serializer dữ liệu sản phẩm & validation
│       ├── tests.py                    # 17 bài kiểm thử tự động cho Service 2
│       ├── urls.py                     # Tuyến đường /products và /products/<id>
│       └── views.py                    # Controller CRUD: List, Create, Retrieve, Update, Delete
│
├── docs/                               # Tài liệu đề bài gốc
│   ├── BÀI THỰC HÀNH SỐ 1.pdf
│   ├── BÀI THỰC HÀNH SỐ 2.pdf
│   └── BÀI THỰC HÀNH SỐ 3.pdf
│
├── run_all_services.bat                # Script chạy đồng thời cả 2 services
├── run_auth_service.bat                # Script chạy riêng Service 1 (Cổng 8000)
├── run_product_service.bat             # Script chạy riêng Service 2 (Cổng 8001)
├── run_tests.bat                       # Script chạy 26 bài test của cả 2 services
├── db.sqlite3                          # Database của Auth Service
├── manage.py                           # CLI của Auth Service
├── requirements.txt                    # Thư viện phụ thuộc (Django, DRF, PyJWT, requests...)
└── README.md                           # Báo cáo và hướng dẫn toàn diện
```

---

## 6. YÊU CẦU MÔI TRƯỜNG & CÔNG NGHỆ SỬ DỤNG

### Công nghệ nền tảng:
- **Python:** Phiên bản `>= 3.10` (Khuyên dùng Python 3.11 hoặc 3.12)
- **Django:** Phiên bản `>= 5.1, < 7.0`
- **Django REST Framework (DRF):** `>= 3.15.0`
- **PyJWT:** `>= 2.8.0` (Thư viện xử lý JSON Web Token)
- **requests:** `>= 2.31.0` (Giao tiếp HTTP giữa các service trong kiến trúc SOA)
- **drf-spectacular:** `>= 0.27.0` (Bộ sinh tài liệu OpenAPI 3.0 & Swagger UI)
- **SQLite3:** Hệ quản trị cơ sở dữ liệu nhúng riêng biệt cho từng service

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

### Bước 3: Đồng bộ Cơ sở dữ liệu (Migration) cho cả 2 Services

Khởi tạo và cập nhật cấu trúc database riêng cho từng service:
```bash
# 1. Đồng bộ bảng User cho Auth Service
python manage.py makemigrations
python manage.py migrate

# 2. Đồng bộ bảng products cho Product Service (Kiến trúc SOA)
python product_service/manage.py makemigrations
python product_service/manage.py migrate
```

---

### Bước 4: Nạp dữ liệu mẫu để kiểm thử (Seed Data)

Dự án tích hợp sẵn 2 câu lệnh tạo nhanh tài khoản và danh sách sản phẩm mẫu:

1. **Tạo tài khoản người dùng mẫu (Auth Service):**
   ```bash
   python manage.py seed_user
   ```
   - **Tài khoản (`userName`):** `testuser`
   - **Mật khẩu gốc (Plain text):** `123456`
   - **Mật khẩu Base64:** `MTIzNDU2`
   - **Mật khẩu băm MD5:** `e10adc3949ba59abbe56e057f20f883e`

2. **Tạo 5 sản phẩm công nghệ mẫu (Product Service):**
   ```bash
   python product_service/manage.py seed_products
   ```
   - Tự động nạp các sản phẩm mẫu: Laptop Dell XPS 15, Bàn phím cơ Keychron Q1 Pro, Chuột Logitech MX Master 3S, v.v.

---

### Bước 5: Khởi động hệ thống (Chạy cả 2 Services)

Bạn có thể lựa chọn 1 trong 2 cách sau:

- **Cách 1 (Nhanh nhất - Khuyên dùng trên Windows):**
  Nhấp đúp chuột vào tệp script:
  ```cmd
  run_all_services.bat
  ```
  Script sẽ tự động mở 2 cửa sổ terminal độc lập:
  - Cửa sổ 1: Auth Service tại `http://localhost:8000` (Swagger: `http://localhost:8000/swagger/`)
  - Cửa sổ 2: Product Service tại `http://localhost:8001` (Swagger: `http://localhost:8001/swagger/`)

- **Cách 2: Khởi động thủ công qua lệnh Terminal riêng biệt:**
  - **Terminal 1 (Auth Service - Cổng 8000):**
    ```bash
    python manage.py runserver 8000
    ```
  - **Terminal 2 (Product Service - Cổng 8001):**
    ```bash
    python product_service/manage.py runserver 8001
    ```

---

## 8. TÀI LIỆU API CHI TIẾT (API DOCUMENTATION)

### Danh sách Endpoint tổng quan:

#### A. DỊCH VỤ 1: AUTHENTICATION SERVICE (`http://localhost:8000`)
| Chức năng | Phương thức | Đường dẫn (URL) | Mô tả tóm tắt | Quyền truy cập |
| :--- | :---: | :--- | :--- | :---: |
| **Login** | `POST` | `/` hoặc `/login` | Đăng nhập và cấp phát chuỗi JWT | Public |
| **Auth** | `GET` / `POST` | `/auth` | Xác thực tính hợp lệ của Token | Public |
| **Hello World** | `GET` | `/hello` hoặc `/api/hello/` | API in dòng `hello-world` |  **Cần Bearer Token** |
| **Register** | `POST` | `/register` | Đăng ký tài khoản người dùng mới | Public |
| **Swagger UI** | `GET` | `/swagger/` hoặc `/docs/` | Giao diện tài liệu Swagger Service 1 | Public |
| **OpenAPI Schema** | `GET` | `/api/schema/` | Tải về cấu hình JSON/YAML OpenAPI | Public |
| **Django Admin** | `GET` | `/admin/` | Trang quản trị dữ liệu User | Cần Superuser |

#### B. DỊCH VỤ 2: PRODUCT MANAGEMENT SERVICE (`http://localhost:8001`)
| Chức năng | Phương thức | Đường dẫn (URL) | Mô tả tóm tắt | Quyền truy cập |
| :--- | :---: | :--- | :--- | :---: |
| **Thông tin Service** | `GET` | `/` | Trạng thái và danh mục API Product | Public |
| **Danh sách sản phẩm** | `GET` | `/products` | Lấy danh sách sản phẩm (hỗ trợ `?search=`) |  **Cần Bearer Token (Auth Service)** |
| **Thêm mới sản phẩm** | `POST` | `/products` | Thêm một sản phẩm mới vào database |  **Cần Bearer Token (Auth Service)** |
| **Chi tiết sản phẩm** | `GET` | `/products/<id>` | Xem chi tiết sản phẩm theo ID |  **Cần Bearer Token (Auth Service)** |
| **Cập nhật sản phẩm** | `PUT` | `/products/<id>` | Cập nhật toàn bộ thông tin sản phẩm |  **Cần Bearer Token (Auth Service)** |
| **Cập nhật từng phần**| `PATCH`| `/products/<id>` | Cập nhật một số trường của sản phẩm |  **Cần Bearer Token (Auth Service)** |
| **Xóa sản phẩm** | `DELETE` | `/products/<id>` | Xóa sản phẩm khỏi database |  **Cần Bearer Token (Auth Service)** |
| **Swagger UI** | `GET` | `/swagger/` hoặc `/docs/` | Giao diện tài liệu Swagger Service 2 | Public |
| **OpenAPI Schema** | `GET` | `/api/schema/` | Tải về cấu hình OpenAPI Service 2 | Public |
| **Django Admin** | `GET` | `/admin/` | Trang quản trị dữ liệu Products | Cần Superuser |

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

#### 8.5. API Danh sách Sản phẩm (GET /products)
- **Phương thức:** `GET`
- **Đường dẫn:** `http://localhost:8001/products` (hoặc `http://localhost:8001/products/`)
- **Yêu cầu:** Header `Authorization: Bearer <token>` (Lấy từ Auth Service)
- **Tham số tùy chọn:** `?search=<từ_khóa>` để lọc theo tên sản phẩm.
- **Phản hồi thành công (`200 OK`):**
  ```json
  {
    "message": "Lấy danh sách sản phẩm thành công.",
    "total": 5,
    "authenticated_user": {
      "id": 1,
      "username": "testuser"
    },
    "data": [
      {
        "id": 1,
        "name": "Laptop Dell XPS 15 9530",
        "description": "Intel Core i7-13700H, 16GB RAM, 512GB SSD...",
        "price": "42500000.00",
        "quantity": 10,
        "created_at": "2026-10-18T04:00:00Z",
        "updated_at": "2026-10-18T04:00:00Z"
      }
    ]
  }
  ```

---

#### 8.6. API Thêm mới Sản phẩm (POST /products)
- **Phương thức:** `POST`
- **Đường dẫn:** `http://localhost:8001/products`
- **Yêu cầu:** Header `Authorization: Bearer <token>`
- **Body JSON:**
  ```json
  {
    "name": "Bàn phím cơ không dây Keychron K2 Pro",
    "description": "Bàn phím cơ Bluetooth layout 75%, hot-swap switch Gateron.",
    "price": "1850000.00",
    "quantity": 25
  }
  ```
- **Phản hồi thành công (`201 Created`):**
  ```json
  {
    "message": "Thêm mới sản phẩm thành công.",
    "authenticated_user": {
      "id": 1,
      "username": "testuser"
    },
    "data": {
      "id": 6,
      "name": "Bàn phím cơ không dây Keychron K2 Pro",
      "description": "Bàn phím cơ Bluetooth layout 75%, hot-swap switch Gateron.",
      "price": "1850000.00",
      "quantity": 25,
      "created_at": "2026-10-18T04:15:00Z",
      "updated_at": "2026-10-18T04:15:00Z"
    }
  }
  ```

---

#### 8.7. API Chi tiết Sản phẩm theo ID (GET /products/:id)
- **Phương thức:** `GET`
- **Đường dẫn:** `http://localhost:8001/products/1`
- **Yêu cầu:** Header `Authorization: Bearer <token>`
- **Phản hồi thành công (`200 OK`):**
  ```json
  {
    "message": "Lấy thông tin chi tiết sản phẩm thành công.",
    "data": {
      "id": 1,
      "name": "Laptop Dell XPS 15 9530",
      "description": "Intel Core i7-13700H, 16GB RAM, 512GB SSD...",
      "price": "42500000.00",
      "quantity": 10,
      "created_at": "2026-10-18T04:00:00Z",
      "updated_at": "2026-10-18T04:00:00Z"
    }
  }
  ```
- **Phản hồi khi không tìm thấy (`404 Not Found`):**
  ```json
  {
    "error": "Not Found",
    "detail": "Không tìm thấy sản phẩm có ID = 999."
  }
  ```

---

#### 8.8. API Cập nhật Sản phẩm (PUT & PATCH /products/:id)
- **Phương thức:** `PUT` (Cập nhật toàn bộ) hoặc `PATCH` (Cập nhật một phần)
- **Đường dẫn:** `http://localhost:8001/products/1`
- **Yêu cầu:** Header `Authorization: Bearer <token>`
- **Body JSON mẫu:**
  ```json
  {
    "price": "41000000.00",
    "quantity": 8
  }
  ```
- **Phản hồi thành công (`200 OK`):**
  ```json
  {
    "message": "Cập nhật thông tin sản phẩm ID = 1 thành công.",
    "data": {
      "id": 1,
      "name": "Laptop Dell XPS 15 9530",
      "price": "41000000.00",
      "quantity": 8,
      "updated_at": "2026-10-18T04:20:00Z"
    }
  }
  ```

---

#### 8.9. API Xóa Sản phẩm (DELETE /products/:id)
- **Phương thức:** `DELETE`
- **Đường dẫn:** `http://localhost:8001/products/1`
- **Yêu cầu:** Header `Authorization: Bearer <token>`
- **Phản hồi thành công (`200 OK`):**
  ```json
  {
    "message": "Đã xóa thành công sản phẩm 'Laptop Dell XPS 15 9530' (ID = 1).",
    "deleted_id": 1
  }
  ```

---

## 9. HƯỚNG DẪN KIỂM THỬ VỚI POSTMAN & SWAGGER UI

### 9.1. Kiểm thử trực quan trên Swagger UI

Hệ thống cung cấp **2 giao diện Swagger UI riêng biệt** cho 2 dịch vụ độc lập:
1. **Auth Service Swagger:** `http://localhost:8000/swagger/`
2. **Product Service Swagger:** `http://localhost:8001/swagger/`

#### Các bước thực hiện:
1. Truy cập Swagger của Auth Service tại `http://localhost:8000/swagger/`.
2. Mở endpoint `POST /` (Login), nhấn **Try it out**, nhập tài khoản `testuser` và mật khẩu `MTIzNDU2`, bấm **Execute** và sao chép mã `token` được trả về.
3. Mở Swagger của Product Service tại `http://localhost:8001/swagger/`.
4. Bấm vào nút **Authorize 🔓** ở góc phải trên cùng của trang:
   - Dán chuỗi `token` vừa sao chép vào ô Value.
   - Nhấn **Authorize** rồi nhấn **Close**.
5. Bây giờ bạn có thể trải nghiệm toàn bộ các thao tác:
   - `GET /products`: Lấy danh sách sản phẩm.
   - `POST /products`: Thêm mới sản phẩm.
   - `GET /products/{pk}`: Lấy chi tiết.
   - `PUT /products/{pk}`: Chỉnh sửa giá hoặc số lượng.
   - `DELETE /products/{pk}`: Xóa sản phẩm.
6. Thử bấm **Logout** trong nút Authorize và gọi lại một API bất kỳ để quan sát hệ thống từ chối với mã lỗi `401 Unauthorized`!

---

### 9.2. Kiểm thử luồng SOA hoàn chỉnh trên Postman
1. **Bước 1 (Auth):** Gửi `POST http://localhost:8000/login` với body:
   ```json
   { "userName": "testuser", "password": "MTIzNDU2" }
   ```
   Lấy chuỗi `token` trong phản hồi.
2. **Bước 2 (Product Service):** Tạo request mới:
   - URL: `http://localhost:8001/products`
   - Tab **Authorization**: Chọn type **Bearer Token**, dán chuỗi token vào.
   - Thử nghiệm gửi request không có token để thấy lỗi 401.
   - Gửi kèm token để thấy danh sách toàn bộ sản phẩm 200 OK.

---

## 10. KIỂM THỬ TỰ ĐỘNG (AUTOMATED UNIT TESTS)

Dự án trang bị bộ kiểm thử tự động toàn diện với **tổng cộng 26 bài test độc lập**:
- **Service 1 (Auth Service):** 9 bài test tại [core/tests.py](file:///d:/CODES/Py/Django_Learning/core/tests.py)
- **Service 2 (Product Service):** 17 bài test tại [product_service/products/tests.py](file:///d:/CODES/Py/Django_Learning/product_service/products/tests.py)

### Chạy toàn bộ 26 tests chỉ với 1 thao tác:
- **Trên Windows:** Nhấp đúp vào tệp script:
  ```cmd
  run_tests.bat
  ```
- **Hoặc chạy qua dòng lệnh:**
  ```powershell
  python manage.py test core
  python product_service/manage.py test products
  ```

### Kết quả chạy kiểm thử thực tế (100% Passed):
```text
[1/2] Kiem thu Service 1 (Auth Service)...
.........
Ran 9 tests in 3.922s
OK

[2/2] Kiem thu Service 2 (Product Service)...
.................
Ran 17 tests in 0.316s
OK

========================================================
  [THANH CONG] TAT CA CAC BAI KIEM THU DA VUOT QUA (OK)
========================================================
```

### Danh mục 17 bài test của Service 2 (Product Service):
1. `test_get_products_without_token_returns_401`: Chặn 401 khi không có token.
2. `test_get_products_with_invalid_token_returns_401`: Chặn 401 khi token giả mạo.
3. `test_get_products_with_expired_token_returns_401`: Chặn 401 khi token đã hết hạn.
4. `test_get_all_products_success`: Lấy danh sách sản phẩm thành công với 200 OK.
5. `test_create_product_success`: Tạo mới sản phẩm thành công với 201 Created.
6. `test_create_product_invalid_price_returns_400`: Chặn 400 khi giá sản phẩm là số âm.
7. `test_create_product_invalid_quantity_returns_400`: Chặn 400 khi số lượng là số âm.
8. `test_create_product_empty_name_returns_400`: Chặn 400 khi tên sản phẩm để trống.
9. `test_get_product_detail_success`: Lấy chi tiết thông tin sản phẩm thành công.
10. `test_get_product_detail_not_found_returns_404`: Trả về 404 khi ID sản phẩm không tồn tại.
11. `test_update_product_put_success`: Cập nhật toàn bộ thông tin sản phẩm thành công.
12. `test_update_product_patch_success`: Cập nhật từng phần thông tin sản phẩm thành công.
13. `test_delete_product_success`: Xóa sản phẩm khỏi database thành công.
14. `test_delete_product_not_found_returns_404`: Trả về 404 khi xóa sản phẩm không tồn tại.
15. `test_auth_service_http_integration_success`: Kiểm thử gọi HTTP xác thực thành công sang Auth Service.
16. `test_auth_service_http_integration_unauthorized`: Kiểm thử xử lý khi Auth Service từ chối xác thực.
17. `test_offline_fallback_jwt_verification`: Kiểm thử cơ chế giải mã JWT dự phòng nội bộ khi Auth Service offline.

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
- **Tài liệu tham chiếu:** [BÀI THỰC HÀNH SỐ 1.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%201.pdf), [BÀI THỰC HÀNH SỐ 2.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%202.pdf) và [BÀI THỰC HÀNH SỐ 3.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%203.pdf)
