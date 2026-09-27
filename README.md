# Django RESTful API - Router, Middleware & Bảo mật với JWT

Dự án triển khai bài thực hành xây dựng **RESTful API** với **Django**, **Django REST Framework (DRF)**, quản lý định tuyến với **Router**, lọc và kiểm soát truy cập bằng **Middleware**, cùng cơ chế xác thực và phân quyền bằng **JSON Web Token (JWT)**.

---

## 📑 Mục lục

1. [Tính năng & Yêu cầu đáp ứng](#-tính-năng--yêu-cầu-đáp-ứng)
2. [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
3. [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
4. [Cấu trúc Cơ sở dữ liệu](#-cấu-trúc-cơ-sở-dữ-liệu)
5. [Hướng dẫn cài đặt & Chạy ứng dụng](#-hướng-dẫn-cài-đặt--chạy-ứng-dụng)
6. [Tài liệu API & Danh sách Endpoints](#-tài-liệu-api--danh-sách-endpoints)
7. [Cơ chế hoạt động chính](#-cơ-chế-hoạt-động-chính)
8. [Chạy Kiểm thử tự động (Unit Tests)](#-chạy-kiểm-thử-tự-động-unit-tests)

---

## 🎯 Tính năng & Yêu cầu đáp ứng

- **Thư viện JWT**: Sử dụng thư viện `PyJWT` chuẩn công nghiệp để sinh và xác thực JSON Web Token.
- **Dịch vụ Đăng nhập (`localhost:8000/` hoặc `/login`)**:
  - Nhận `userName` và `password` (hỗ trợ mật khẩu gửi lên dạng **Base64**, **MD5**, hoặc plain text).
  - So khớp với mật khẩu lưu trong DB, phát hành chuỗi JWT và lưu trực tiếp vào trường `Token` của bảng `User`.
- **Dịch vụ Xác thực Token (`localhost:8000/auth`)**:
  - Kiểm tra chữ ký, tính toàn vẹn và hạn sử dụng (`exp`) của Token.
  - Hỗ trợ truyền Token qua Header `Authorization: Bearer <token>`, Body `{"token": "..."}`, hoặc query `?token=...`.
- **Middleware kiểm soát truy cập (`JWTAuthenticationMiddleware`)**:
  - Lắng nghe các request gọi đến API in dòng `Hello World` (`/hello` hoặc `/api/hello/`).
  - Tự động chặn truy cập (`401 Unauthorized`) nếu thiếu Token hoặc Token không hợp lệ.
  - Cho phép truy cập (`200 OK`) kèm thông tin người dùng đã xác thực nếu Token hợp lệ.
- **Tài liệu trực quan Swagger UI**:
  - Tích hợp OpenAPI 3.0 với `drf-spectacular` tại `/swagger/` và `/docs/`, hỗ trợ kiểm thử trực tiếp trên trình duyệt.

---

## 🛠 Công nghệ sử dụng

- **Ngôn ngữ**: Python 3.10+
- **Framework**: Django 5.x / 6.x & Django REST Framework (DRF)
- **Bảo mật & JWT**: PyJWT
- **Tài liệu API**: drf-spectacular (OpenAPI 3.0 / Swagger UI)
- **Cơ sở dữ liệu**: SQLite3 (mặc định)

---

## 📂 Cấu trúc thư mục

```text
Django_Learning/
│
├── core/                           # Ứng dụng chính (Core App)
│   ├── management/commands/        # Lệnh tùy chỉnh Django
│   │   └── seed_user.py            # Script khởi tạo tài khoản mẫu kiểm thử
│   ├── migrations/                 # Lịch sử lược đồ cơ sở dữ liệu
│   │   └── 0001_initial.py         # Migration bảng User
│   ├── models.py                   # Bảng User theo phụ lục đề bài
│   ├── middleware.py               # JWTAuthenticationMiddleware kiểm soát /hello
│   ├── serializers.py              # Serializers xác thực dữ liệu đầu vào
│   ├── utils.py                    # Logic sinh/giải mã JWT & xử lý mật khẩu Base64/MD5
│   ├── views.py                    # Views xử lý login, auth, hello_world, register
│   ├── urls.py                     # Định tuyến nội bộ cho app core
│   └── tests.py                    # 9 Test cases kiểm thử tự động toàn diện
│
├── myapi/                          # Cấu hình dự án Django
│   ├── settings.py                 # Cấu hình INSTALLED_APPS, MIDDLEWARE, SPECTACULAR
│   └── urls.py                     # Định tuyến gốc (root routing & Swagger)
│
├── docs/                           # Tài liệu đề bài thực hành
│   └── BÀI THỰC HÀNH SỐ 2.pdf
│
├── manage.py                       # Điểm vào thực thi Django
├── requirements.txt                # Danh sách thư viện phụ thuộc
└── README.md                       # Hướng dẫn chi tiết dự án
```

---

## 🗄 Cấu trúc Cơ sở dữ liệu

Bảng **`User`** được triển khai theo đúng phụ lục đề bài:

| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `IdUser` | `INT` / `AutoField` | **PRIMARY KEY** | Mã định danh tự tăng của người dùng |
| `UserName` | `VARCHAR(255)` | `UNIQUE` | Tên tài khoản hoặc email đăng nhập |
| `Password` | `VARCHAR(255)` | `NOT NULL` | Mật khẩu (lưu trữ mã băm MD5 an toàn) |
| `Token` | `VARCHAR(255)` | `NULLABLE` | Lưu chuỗi JWT được cấp phát sau khi đăng nhập |

> **Ghi chú về JWT Payload:** Chuỗi JWT được thiết kế tối ưu kích thước payload (`id`, `username`, `iat`, `exp` ~ 140-160 ký tự) nhằm đảm bảo hoàn toàn vừa vặn trong giới hạn `VARCHAR(255)` của cột `Token`.

---

## 🚀 Hướng dẫn cài đặt & Chạy ứng dụng

### 1. Chuẩn bị môi trường ảo

- **Mở Terminal tại thư mục dự án và kích hoạt môi trường ảo:**

  - *Trên Windows (PowerShell):*
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
  - *Trên Windows (CMD):*
    ```cmd
    venv\Scripts\activate.bat
    ```
  - *Trên macOS / Linux:*
    ```bash
    source venv/bin/activate
    ```

- **Cài đặt các gói phụ thuộc (nếu cài mới):**
  ```bash
  pip install -r requirements.txt
  ```

### 2. Cập nhật Cơ sở dữ liệu

```bash
python manage.py migrate
```

### 3. Khởi tạo tài khoản mẫu (Seed Data)

Dự án cung cấp sẵn lệnh tạo nhanh tài khoản kiểm thử:

```bash
python manage.py seed_user
```

**Thông tin tài khoản mẫu:**
- **Tên đăng nhập (`userName`):** `testuser`
- **Mật khẩu gốc:** `123456`
- **Mật khẩu Base64:** `MTIzNDU2`
- **Mật khẩu MD5:** `e10adc3949ba59abbe56e057f20f883e`

### 4. Khởi chạy máy chủ phát triển

```bash
python manage.py runserver
```

Truy cập API tại: `http://localhost:8000/`  
Giao diện Swagger UI: `http://localhost:8000/swagger/` hoặc `http://localhost:8000/docs/`

---

## 📖 Tài liệu API & Danh sách Endpoints

| Phương thức | Endpoint | Mô tả | Yêu cầu xác thực |
| :---: | :--- | :--- | :---: |
| `POST` | `/` hoặc `/login` | Đăng nhập và nhận chuỗi JWT Token | ❌ Không |
| `GET` / `POST` | `/auth` | Xác thực tính hợp lệ của JWT Token | ❌ Không |
| `GET` | `/hello` hoặc `/api/hello/` | API in dòng "Hello World" từ Bài 1 |  **Bắt buộc JWT** |
| `POST` | `/register` | Đăng ký tài khoản người dùng mới | ❌ Không |
| `GET` | `/swagger/` | Giao diện tài liệu tương tác Swagger UI | ❌ Không |

---

### Chi tiết các API chính

#### 1. Đăng nhập (Login)
- **URL:** `POST http://localhost:8000/` hoặc `http://localhost:8000/login`
- **Body JSON (Hỗ trợ 1 trong 3 dạng mật khẩu):**
  ```json
  {
    "userName": "testuser",
    "password": "MTIzNDU2"
  }
  ```
  *(Hoặc dùng MD5: `"password": "e10adc3949ba59abbe56e057f20f883e"`)*
- **Response thành công (`200 OK`):**
  ```json
  {
    "message": "Đăng nhập thành công",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "IdUser": 1,
      "UserName": "testuser"
    }
  }
  ```

#### 2. Xác thực Token (Auth)
- **URL:** `GET http://localhost:8000/auth` hoặc `POST http://localhost:8000/auth`
- **Header:** `Authorization: Bearer <chuỗi_token_nhận_được>`
  *(Hoặc gửi qua POST body: `{"token": "<chuỗi_token>"}`)*
- **Response thành công (`200 OK`):**
  ```json
  {
    "valid": true,
    "message": "Token hợp lệ và còn hiệu lực.",
    "payload": {
      "id": 1,
      "username": "testuser",
      "exp": 1789961919,
      "iat": 1789954719
    },
    "user": {
      "IdUser": 1,
      "UserName": "testuser",
      "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  }
  ```

#### 3. API Hello World (Có Middleware bảo vệ)
- **URL:** `GET http://localhost:8000/hello` hoặc `http://localhost:8000/api/hello/`
- **Header:** `Authorization: Bearer <chuỗi_token_hợp_lệ>`
- **Response thành công (`200 OK`):**
  ```json
  {
    "message": "hello-world",
    "authenticated_user": {
      "IdUser": 1,
      "UserName": "testuser"
    }
  }
  ```
- **Response khi thiếu hoặc sai Token (`401 Unauthorized`):**
  ```json
  {
    "error": "Unauthorized",
    "detail": "Vui lòng cung cấp JWT token qua Header 'Authorization: Bearer <token>' để truy cập API này."
  }
  ```

---

## ⚙️ Cơ chế hoạt động chính

### 1. Xử lý mật khẩu Client linh hoạt (`verify_password`)
Nhằm phục vụ đúng yêu cầu đề bài *"Mật khẩu đã mã hoá base64 hoặc Md5 tại client"*, hàm `verify_password` tại `core/utils.py` thực hiện:
- Kiểm tra giải mã Base64 sang chuỗi gốc rồi so sánh với mã băm trong DB.
- So sánh trực tiếp chuỗi mã băm MD5 32 ký tự nếu client chủ động băm MD5 trước khi gửi.
- Hỗ trợ plain text phục vụ cho các trường hợp kiểm thử nhanh.

### 2. Quản lý vòng đời Token JWT
- **Cấp phát:** Token được ký bằng thuật toán `HS256` cùng `SECRET_KEY` của ứng dụng Django, thời hạn hiệu lực mặc định là **2 giờ**.
- **Lưu trữ:** Token vừa tạo lập tức được cập nhật vào trường `Token` của bản ghi người dùng trong bảng `User`.
- **Giải mã & Kiểm tra:** Xử lý bắt các ngoại lệ chuẩn của PyJWT: `ExpiredSignatureError` (hết hạn), `InvalidSignatureError` (sai khóa bí mật), `DecodeError` (sai cấu trúc token).

### 3. Middleware bảo vệ tầng mạng (`JWTAuthenticationMiddleware`)
- Chặn trước khi request chạm tới view `hello_world`.
- Tách chuỗi từ Header `Authorization: Bearer ...`.
- Nạp thông tin đối tượng người dùng vào `request.jwt_user` để các view phía sau tái sử dụng mà không cần truy vấn lại nhiều lần.

---

## 🧪 Chạy Kiểm thử tự động (Unit Tests)

Dự án đi kèm bộ test tự động (`APITestCase`) kiểm tra đầy đủ mọi yêu cầu của đề bài:

```powershell
python manage.py test
```

### Danh sách 9 kịch bản test:
1. `test_01_login_with_base64_password`: Kiểm tra đăng nhập với mật khẩu Base64 & xác nhận lưu token vào DB.
2. `test_02_login_with_md5_password`: Kiểm tra đăng nhập với mật khẩu MD5.
3. `test_03_login_with_plain_password`: Kiểm tra đăng nhập với mật khẩu văn bản gốc.
4. `test_04_login_wrong_password`: Xác nhận trả về lỗi 401 khi sai mật khẩu.
5. `test_05_auth_token_endpoint`: Kiểm tra API `/auth` xác thực token qua Header và Body.
6. `test_06_middleware_blocks_hello_world_without_token`: Middleware chặn `/hello` khi thiếu token.
7. `test_07_middleware_blocks_hello_world_with_invalid_token`: Middleware chặn `/hello` khi token giả/sai.
8. `test_08_middleware_allows_hello_world_with_valid_token`: Middleware mở quyền truy cập `/hello` khi token hợp lệ.
9. `test_09_register_endpoint`: Kiểm tra API đăng ký người dùng mới.
