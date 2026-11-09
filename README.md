# 🚀 BÁO CÁO & HƯỚNG DẪN DỰ ÁN DJANGO RESTFUL API
## Học phần: Phát triển Dịch vụ Web / RESTful API
> **Bài Thực Hành Số 1:** Cài đặt và cấu hình môi trường xây dựng API ("Hello World")  
> **Bài Thực Hành Số 2:** Router, Middleware và Bảo mật với JWT trong RESTful API  
> **Bài Thực Hành Số 3:** Xây dựng Dịch vụ Quản lý Sản phẩm theo Kiến trúc Hướng Dịch vụ (SOA)  
> **Bài Thực Hành Số 4:** Xây dựng Dịch vụ Quản lý Đơn hàng theo Kiến trúc Hướng Dịch vụ (SOA)  
> **Bài Thực Hành Số 5:** Xây dựng Dịch vụ Báo cáo & Thống kê theo Kiến trúc Hướng Dịch vụ (SOA)  

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

Dự án tích hợp đầy đủ nội dung của **cả 5 bài thực hành**:
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
- **Bài thực hành số 4:** Xây dựng **Order Management Service (Cổng 8002)** độc lập theo kiến trúc **SOA**:
  - Chạy trên một cổng riêng (`localhost:8002/`) và cơ sở dữ liệu SQLite riêng (`orders_db.sqlite3`).
  - Bảng đơn hàng (`orders`) và chi tiết đơn hàng (`order_items`).
  - Bộ RESTful API CRUD hoàn chỉnh cho đơn hàng (`/orders`, `/orders/:id`) và chi tiết mặt hàng (`/order_items`, `/order_items/:id`).
  - Cơ chế xác thực liên dịch vụ: Thẩm định JWT thông qua Auth Service (`http://127.0.0.1:8000/auth`).
  - Kiểm tra và đồng bộ tồn kho liên dịch vụ: Tự động kiểm tra số lượng tồn kho và đơn giá từ Product Service (`http://127.0.0.1:8001/products`), trừ tồn kho khi đặt hàng và hoàn tồn kho khi hủy đơn hoặc xóa mặt hàng.
  - Tích hợp tài liệu tương tác Swagger UI tại `http://localhost:8002/swagger/`.
- **Bài thực hành số 5:** Xây dựng **Reporting Service (Cổng 8003)** độc lập theo kiến trúc **SOA**:
  - Chạy trên một cổng riêng (`localhost:8003/`) và cơ sở dữ liệu SQLite riêng (`reports_db.sqlite3`).
  - Bảng báo cáo đơn hàng (`orders_reports`) và bảng báo cáo sản phẩm (`product_reports`).
  - Bộ RESTful API thống kê doanh thu, chi phí, lợi nhuận theo đơn hàng (`/reports/orders`, `/reports/orders/:id`) và sản phẩm (`/reports/products`, `/reports/products/:id`).
  - Cơ chế tích hợp dữ liệu liên dịch vụ: Tự động tổng hợp số liệu từ Order Service (`http://127.0.0.1:8002/orders`) và Product Service (`http://127.0.0.1:8001/products`).
  - Thẩm định quyền truy cập thông qua Auth Service (`http://127.0.0.1:8000/auth`).
  - Tích hợp tài liệu tương tác Swagger UI tại `http://localhost:8003/swagger/`.

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

### Đối chiếu Bài Thực Hành Số 4:
| Yêu cầu trong PDF Bài 4 | Tình trạng | Vị trí triển khai trong Codebase |
| :--- | :---: | :--- |
| **1. Khởi tạo một cổng mới cho service (`localhost:***2/`)** |  **100% Đạt** | Service quản lý đơn hàng chạy độc lập trên cổng `8002` (`http://localhost:8002/`). Script khởi chạy riêng [run_order_service.bat](file:///d:/CODES/Py/Django_Learning/run_order_service.bat). |
| **2. Cơ sở dữ liệu riêng biệt theo nguyên tắc SOA** |  **100% Đạt** | Tách cơ sở dữ liệu riêng `order_service/orders_db.sqlite3` không dùng chung file hay bảng với Auth và Product Service. |
| **3. Bảng đơn hàng (`orders`) theo Phụ lục**<br>- `id`: INT (PK)<br>- `customer_name`: VARCHAR(255)<br>- `customer_email`: VARCHAR(255)<br>- `total_amount`: DECIMAL(10, 2)<br>- `status`: VARCHAR(50) (pending, completed, cancelled)<br>- `created_at`: TIMESTAMP<br>- `updated_at`: TIMESTAMP |  **100% Đạt** | Model `Order` tại [order_service/orders/models.py](file:///d:/CODES/Py/Django_Learning/order_service/orders/models.py#L5). Đã tạo migration `0001_initial.py` và đăng ký trong Django Admin [order_service/orders/admin.py](file:///d:/CODES/Py/Django_Learning/order_service/orders/admin.py). |
| **4. Bảng chi tiết đơn hàng (`order_items`) theo Phụ lục**<br>- `id`: INT (PK)<br>- `order_id`: INT (FK `orders`)<br>- `product_id`: INT (lưu vết Product Service)<br>- `product_name`: VARCHAR(255)<br>- `quantity`: INT<br>- `unit_price`: DECIMAL(10, 2)<br>- `total_price`: DECIMAL(10, 2) |  **100% Đạt** | Model `OrderItem` tại [order_service/orders/models.py](file:///d:/CODES/Py/Django_Learning/order_service/orders/models.py#L80). Tự động tính toán `total_price = quantity * unit_price` và cập nhật lại `total_amount` của `Order`. |
| **5. RESTful API `GET /orders` & `GET /orders/:id`** |  **100% Đạt** | Triển khai tại [order_service/orders/views.py](file:///d:/CODES/Py/Django_Learning/order_service/orders/views.py). Hỗ trợ lọc theo trạng thái (`?status=...`) và tìm kiếm (`?search=...`). |
| **6. RESTful API `POST /orders` (Kiểm tra tồn kho)** |  **100% Đạt** | Tạo đơn hàng mới, tự động gọi sang Product Service để kiểm tra tồn kho (`check_stock`) và trừ tồn kho (`deduct_stock`). Trả về 400 nếu không đủ tồn kho. |
| **7. RESTful API `PUT /orders/:id` (Cập nhật trạng thái)** |  **100% Đạt** | Cập nhật trạng thái đơn hàng (`pending`, `completed`, `cancelled`). Nếu chuyển sang `cancelled`, tự động hoàn trả số lượng tồn kho về Product Service (`restore_stock`). |
| **8. RESTful API `DELETE /orders/:id` (Xóa đơn hàng)** |  **100% Đạt** | Xóa đơn hàng và tự động hoàn trả tồn kho cho các sản phẩm nếu đơn hàng chưa bị hủy. |
| **9. RESTful API Chi tiết đơn hàng (`GET/POST/PUT/DELETE /order_items`)** |  **100% Đạt** | Đầy đủ bộ CRUD cho `order_items`, tự động đồng bộ tồn kho sang Product Service và tính lại `total_amount` của đơn hàng cha. |
| **10. Xác thực qua service ở Bài thực hành số 2** |  **100% Đạt** | Lớp xác thực [AuthServiceAuthentication](file:///d:/CODES/Py/Django_Learning/order_service/orders/authentication.py) thẩm định token JWT qua `http://127.0.0.1:8000/auth`. |
| **11. Swagger UI & Kiểm thử tự động** |  **100% Đạt** | Giao diện tương tác Swagger UI tại `http://localhost:8002/swagger/`. Bộ 23 bài Unit & Integration Tests đạt 100% tại [order_service/orders/tests.py](file:///d:/CODES/Py/Django_Learning/order_service/orders/tests.py). |

### Đối chiếu Bài Thực Hành Số 5:
| Yêu cầu trong PDF Bài 5 | Tình trạng | Vị trí triển khai trong Codebase |
| :--- | :---: | :--- |
| **1. Khởi tạo một cổng mới cho service (`localhost:***3/`)** |  **100% Đạt** | Service báo cáo chạy độc lập trên cổng `8003` (`http://localhost:8003/`). Script khởi chạy riêng [run_report_service.bat](file:///d:/CODES/Py/Django_Learning/run_report_service.bat). |
| **2. Cơ sở dữ liệu riêng biệt theo nguyên tắc SOA** |  **100% Đạt** | Tách cơ sở dữ liệu riêng `report_service/reports_db.sqlite3` không dùng chung bảng hay file với các service khác. |
| **3. Bảng báo cáo đơn hàng (`orders_reports`) theo Phụ lục**<br>- `id`: INT (PK)<br>- `order_id`: INT (lưu vết Order Service)<br>- `total_revenue`: DECIMAL(10, 2)<br>- `total_cost`: DECIMAL(10, 2)<br>- `total_profit`: DECIMAL(10, 2) |  **100% Đạt** | Model `OrderReport` tại [report_service/reports/models.py](file:///d:/CODES/Py/Django_Learning/report_service/reports/models.py#L5). Tự động tính `total_profit = total_revenue - total_cost`. Đã migrate và đăng ký Django Admin [report_service/reports/admin.py](file:///d:/CODES/Py/Django_Learning/report_service/reports/admin.py). |
| **4. Bảng báo cáo sản phẩm (`product_reports`) theo Phụ lục**<br>- `id`: INT (PK)<br>- `order_report_id`: INT (FK `orders_reports`)<br>- `product_id`: INT (lưu vết Product Service)<br>- `total_sold`: INT<br>- `revenue`: DECIMAL(10, 2)<br>- `cost`: DECIMAL(10, 2)<br>- `profit`: DECIMAL(10, 2) |  **100% Đạt** | Model `ProductReport` tại [report_service/reports/models.py](file:///d:/CODES/Py/Django_Learning/report_service/reports/models.py#L65). Tự động tính `profit = revenue - cost`. |
| **5. RESTful API `GET /reports/orders` & `GET /reports/orders/:id`** |  **100% Đạt** | Triển khai tại [report_service/reports/views.py](file:///d:/CODES/Py/Django_Learning/report_service/reports/views.py). Hỗ trợ lọc theo `?order_id=`. |
| **6. RESTful API `POST /reports/orders`** |  **100% Đạt** | Tạo báo cáo đơn hàng mới dựa trên dữ liệu từ Order Service (cổng 8002), tự động tạo các bản ghi `product_reports` tương ứng từ items của đơn hàng. |
| **7. RESTful API `DELETE /reports/orders/:id`** |  **100% Đạt** | Xóa báo cáo đơn hàng (cascade xóa các báo cáo sản phẩm con). |
| **8. RESTful API `GET /reports/products` & `GET /reports/products/:id`** |  **100% Đạt** | Lấy danh sách hoặc chi tiết báo cáo theo sản phẩm (hỗ trợ lọc `?product_id=`). |
| **9. RESTful API `POST /reports/products`** |  **100% Đạt** | Tạo báo cáo sản phẩm mới dựa trên dữ liệu từ Product Service (8001) và Order Service (8002). |
| **10. RESTful API `DELETE /reports/products/:id`** |  **100% Đạt** | Xóa báo cáo sản phẩm khỏi database. |
| **11. Xác thực qua service ở Bài thực hành số 2** |  **100% Đạt** | Lớp xác thực [AuthServiceAuthentication](file:///d:/CODES/Py/Django_Learning/report_service/reports/authentication.py) thẩm định token JWT qua `http://127.0.0.1:8000/auth`. |
| **12. Swagger UI & Kiểm thử tự động** |  **100% Đạt** | Giao diện tương tác Swagger UI tại `http://localhost:8003/swagger/`. Bộ 21 bài Unit & Integration Tests đạt 100% tại [report_service/reports/tests.py](file:///d:/CODES/Py/Django_Learning/report_service/reports/tests.py). |

---

## 3. KIẾN TRÚC HỆ THỐNG & LUỒNG XỬ LÝ (WORKFLOW SOA)

### 3.1. Sơ đồ kiến trúc SOA (Kiến trúc hướng dịch vụ 4 Services độc lập)
```text
+----------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                      CLIENT (Postman / Browser / Swagger UI)                                                       |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
           |                                             |                                               |                             |
  (1) POST /login (lấy JWT)                     (3) CRUD Sản phẩm                               (5) CRUD Đơn hàng             (7) Xem & Tạo Báo cáo
  http://localhost:8000/login                   http://localhost:8001/products                  http://localhost:8002/orders  http://localhost:8003/reports
           |                                             |                                               |                             |
           v                                             v                                               v                             v
+-------------------------------+             +-------------------------------+               +-------------------------------+   +-------------------------------+
|    DỊCH VỤ 1: AUTH SERVICE    |             |  DỊCH VỤ 2: PRODUCT SERVICE   |               |   DỊCH VỤ 3: ORDER SERVICE    |   |  DỊCH VỤ 4: REPORTING SERVICE |
|     (Chạy tại cổng :8000)     |  (4) /auth  |     (Chạy tại cổng :8001)     | (6b) check/   |     (Chạy tại cổng :8002)     |   |     (Chạy tại cổng :8003)     |
|                               |<------------|                               |<--------------|                               |   |                               |
| - Cấp phát & Thẩm định JWT    |  (Xác thực) | - CRUD Danh mục Sản phẩm      | deduct/restore| - CRUD Đơn hàng & Mặt hàng    |   | - Thống kê Doanh thu, Chi phí |
| - Middleware bảo vệ API       |             | - Kiểm tra & trừ tồn kho      | tồn kho SP    | - Tính tổng tiền tự động      |   |   và Lợi nhuận theo SP/Đơn    |
| - DB: db.sqlite3 (User)       |<------------------------------------------------------------| - DB: orders_db.sqlite3       |   | - DB: reports_db.sqlite3      |
| - Swagger: :8000/swagger/     |                                 (6a) POST /auth (Xác thực)  | - Swagger: :8002/swagger/     |   | - Swagger: :8003/swagger/     |
+-------------------------------+                                                             +-------------------------------+   +-------------------------------+
           ^                                                                                                  ^                                  |
           |==================================================================================================|==================================|
                                                        (8) POST /auth (Xác thực JWT) & GET /orders, /products
```

### 3.2. Luồng xử lý nghiệp vụ liên dịch vụ (Inter-Service Workflow)
1. **Bước 1 (Đăng nhập):** Client gửi `POST http://localhost:8000/login` lấy token JWT từ Auth Service.
2. **Bước 2 (Quản lý Sản phẩm & Đơn hàng):** Client thực hiện tạo sản phẩm trên Product Service (8001) và tạo đơn hàng trên Order Service (8002).
3. **Bước 3 (Tạo báo cáo tự động):** Client gửi `POST http://localhost:8003/reports/orders` kèm token và `order_id`:
   - Reporting Service tự động gửi request sang Auth Service (`http://127.0.0.1:8000/auth`) để xác thực token.
   - Reporting Service gọi sang Order Service (`http://127.0.0.1:8002/orders/<order_id>`) để lấy tổng doanh thu và danh sách các mặt hàng đã mua.
   - Hệ thống tự động tính toán chi phí vốn, lợi nhuận ròng (`total_profit = total_revenue - total_cost`), lưu vào bảng `orders_reports` và tự động sinh các dòng `product_reports` chi tiết.
2. **Bước 2 (Đặt đơn hàng):** Client gửi `POST http://localhost:8002/orders` kèm `Authorization: Bearer <token>` và danh sách sản phẩm cần mua (`items`).
3. **Bước 3 (Xác thực danh tính):** Order Service tự động gọi `POST http://127.0.0.1:8000/auth` để xác thực token.
4. **Bước 4 (Kiểm tra tồn kho):** Order Service gọi `GET http://127.0.0.1:8001/products/<id>` để kiểm tra số lượng tồn kho `quantity` của từng sản phẩm.
   - Nếu tồn kho không đủ: Order Service trả về `400 Bad Request` nêu rõ lý do.
   - Nếu đủ tồn kho: Tiếp tục bước 5.
5. **Bước 5 (Tạo đơn hàng & Trừ tồn kho):** Order Service ghi nhận đơn hàng và các mặt hàng trong cơ sở dữ liệu `orders_db.sqlite3` trong một giao dịch nguyên tử (`transaction.atomic`), sau đó gọi `PATCH http://127.0.0.1:8001/products/<id>` để trừ số lượng tồn kho trên Product Service.
6. **Bước 6 (Hủy đơn hàng / Hoàn kho):** Khi đơn hàng bị hủy (`status = cancelled`) hoặc bị xóa, Order Service tự động gọi hoàn lại số lượng tồn kho tương ứng về Product Service.
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

### 4.3. Bảng `orders` & `order_items` (Order Service - file `order_service/orders_db.sqlite3`)

#### Bảng `orders` (Đơn hàng):
```python
class Order(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    customer_name = models.CharField(max_length=255, db_column='customer_name')
    customer_email = models.CharField(max_length=255, db_column='customer_email')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='total_amount')
    status = models.CharField(max_length=50, default='pending', db_column='status')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')
```

| Tên trường (Column) | Kiểu dữ liệu | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`id`** | `INT` (`AutoField`) | **PRIMARY KEY**, Auto Increment | ID duy nhất của đơn hàng |
| **`customer_name`** | `VARCHAR(255)` | `NOT NULL` | Tên khách hàng đặt đơn |
| **`customer_email`** | `VARCHAR(255)` | `NOT NULL` | Email liên hệ của khách hàng |
| **`total_amount`** | `DECIMAL(10, 2)` | `DEFAULT 0.00` | Tổng giá trị đơn hàng (tự động cộng dồn từ items) |
| **`status`** | `VARCHAR(50)` | `pending`, `completed`, `cancelled` | Trạng thái hiện tại của đơn hàng |
| **`created_at`** | `TIMESTAMP` | `auto_now_add=True` | Thời điểm đơn hàng được tạo |
| **`updated_at`** | `TIMESTAMP` | `auto_now=True` | Thời điểm đơn hàng cập nhật gần nhất |

#### Bảng `order_items` (Chi tiết mặt hàng trong đơn):
```python
class OrderItem(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', db_column='order_id')
    product_id = models.IntegerField(db_column='product_id')
    product_name = models.CharField(max_length=255, db_column='product_name')
    quantity = models.IntegerField(default=1, db_column='quantity')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, db_column='unit_price')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, db_column='total_price')
```

| Tên trường (Column) | Kiểu dữ liệu | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`id`** | `INT` (`AutoField`) | **PRIMARY KEY**, Auto Increment | ID duy nhất của chi tiết đơn hàng |
| **`order_id`** | `INT` | `FOREIGN KEY` (`orders.id`) | Liên kết tới đơn hàng cha |
| **`product_id`** | `INT` | `NOT NULL` | Lưu vết ID sản phẩm từ Product Service |
| **`product_name`** | `VARCHAR(255)` | `NOT NULL` | Tên sản phẩm tại thời điểm mua |
| **`quantity`** | `INT` | `DEFAULT 1`, `>= 1` | Số lượng sản phẩm mua |
| **`unit_price`** | `DECIMAL(10, 2)` | `NOT NULL` | Đơn giá tại thời điểm đặt hàng |
| **`total_price`** | `DECIMAL(10, 2)` | `quantity * unit_price` | Thành tiền từng mặt hàng |

### 4.4. Bảng `orders_reports` & `product_reports` (Reporting Service - file `report_service/reports_db.sqlite3`)

#### Bảng `orders_reports` (Báo cáo theo đơn hàng):
```python
class OrderReport(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    order_id = models.IntegerField(db_column='order_id')
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='total_revenue')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='total_cost')
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='total_profit')
```

| Tên trường (Column) | Kiểu dữ liệu | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`id`** | `INT` (`AutoField`) | **PRIMARY KEY**, Auto Increment | ID duy nhất của báo cáo đơn hàng |
| **`order_id`** | `INT` | `NOT NULL` | ID đơn hàng liên kết từ Order Service |
| **`total_revenue`** | `DECIMAL(10, 2)` | `DEFAULT 0.00` | Tổng doanh thu của đơn hàng |
| **`total_cost`** | `DECIMAL(10, 2)` | `DEFAULT 0.00` | Tổng chi phí nhập sản phẩm trong đơn hàng |
| **`total_profit`** | `DECIMAL(10, 2)` | `total_revenue - total_cost` | Tổng lợi nhuận từ đơn hàng |

#### Bảng `product_reports` (Báo cáo theo sản phẩm):
```python
class ProductReport(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    order_report = models.ForeignKey(OrderReport, on_delete=models.CASCADE, related_name='product_reports', db_column='order_report_id', null=True, blank=True)
    product_id = models.IntegerField(db_column='product_id')
    total_sold = models.IntegerField(default=0, db_column='total_sold')
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='revenue')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='cost')
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_column='profit')
```

| Tên trường (Column) | Kiểu dữ liệu | Thuộc tính / Ràng buộc | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **`id`** | `INT` (`AutoField`) | **PRIMARY KEY**, Auto Increment | ID duy nhất của báo cáo sản phẩm |
| **`order_report_id`** | `INT` | `FOREIGN KEY` (`orders_reports.id`) | Liên kết báo cáo đơn hàng (nếu có) |
| **`product_id`** | `INT` | `NOT NULL` | ID sản phẩm liên kết từ Product Service |
| **`total_sold`** | `INT` | `DEFAULT 0`, `>= 0` | Tổng số lượng sản phẩm đã bán |
| **`revenue`** | `DECIMAL(10, 2)` | `DEFAULT 0.00` | Doanh thu từ sản phẩm |
| **`cost`** | `DECIMAL(10, 2)` | `DEFAULT 0.00` | Chi phí nhập sản phẩm |
| **`profit`** | `DECIMAL(10, 2)` | `revenue - cost` | Lợi nhuận từ sản phẩm |

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
├── order_service/                      # SERVICE 3: Quản lý Đơn hàng (Bài 4 - SOA)
│   ├── manage.py                       # CLI riêng cho Order Service (Port 8002)
│   ├── orders_db.sqlite3               # Database SQLite riêng biệt của Order Service
│   ├── schema.yml                      # OpenAPI 3.0 Schema file
│   ├── order_project/                  # Cấu hình dự án Service 3
│   │   ├── settings.py                 # DB riêng, AUTH & PRODUCT service URLs, Swagger :8002
│   │   ├── urls.py                     # Định tuyến /orders, /order_items, /swagger :8002
│   │   ├── asgi.py & wsgi.py
│   └── orders/                         # Ứng dụng Đơn hàng
│       ├── management/commands/seed_orders.py # Lệnh tạo dữ liệu đơn hàng mẫu
│       ├── migrations/0001_initial.py  # Schema bảng orders và order_items
│       ├── admin.py                    # Quản trị Order & OrderItem trong Django Admin :8002
│       ├── authentication.py           # Xác thực liên dịch vụ sang Service 1 (:8000/auth)
│       ├── product_client.py           # Giao tiếp kiểm tra/trừ/hoàn tồn kho sang Service 2 (:8001)
│       ├── models.py                   # Model Order & OrderItem theo Phụ lục Bài 4
│       ├── serializers.py              # Serializer dữ liệu đơn hàng & chi tiết mặt hàng
│       ├── tests.py                    # 23 bài kiểm thử tự động cho Service 3
│       ├── urls.py                     # Tuyến đường /orders và /order_items
│       └── views.py                    # Controller CRUD Order & OrderItem (Kiểm tra tồn kho)
│
├── report_service/                     # SERVICE 4: Báo cáo & Thống kê (Bài 5 - SOA)
│   ├── manage.py                       # CLI riêng cho Reporting Service (Port 8003)
│   ├── reports_db.sqlite3              # Database SQLite riêng biệt của Reporting Service
│   ├── report_project/                 # Cấu hình dự án Service 4
│   │   ├── settings.py                 # DB riêng, AUTH, PRODUCT, ORDER URLs, Swagger :8003
│   │   ├── urls.py                     # Định tuyến /reports/..., /swagger :8003
│   │   ├── asgi.py & wsgi.py
│   └── reports/                        # Ứng dụng Báo cáo
│       ├── management/commands/seed_reports.py # Lệnh tạo dữ liệu báo cáo mẫu
│       ├── migrations/0001_initial.py  # Schema bảng orders_reports và product_reports
│       ├── admin.py                    # Quản trị Báo cáo trong Django Admin :8003
│       ├── authentication.py           # Xác thực liên dịch vụ sang Service 1 (:8000/auth)
│       ├── service_clients.py          # Kết nối Order Service (8002) và Product Service (8001)
│       ├── models.py                   # Model OrderReport & ProductReport theo Phụ lục Bài 5
│       ├── serializers.py              # Serializer dữ liệu báo cáo đơn hàng & sản phẩm
│       ├── tests.py                    # 21 bài kiểm thử tự động cho Service 4
│       ├── urls.py                     # Tuyến đường /reports/orders và /reports/products
│       └── views.py                    # Controller thống kê doanh thu, chi phí, lợi nhuận
│
├── docs/                               # Tài liệu đề bài gốc
│   ├── BÀI THỰC HÀNH SỐ 1.pdf
│   ├── BÀI THỰC HÀNH SỐ 2.pdf
│   ├── BÀI THỰC HÀNH SỐ 3.pdf
│   ├── BÀI THỰC HÀNH SỐ 4.pdf
│   └── BÀI THỰC HÀNH SỐ 5.pdf
│
├── run_all_services.bat                # Script chạy đồng thời cả 4 services (Port 8000, 8001, 8002, 8003)
├── run_auth_service.bat                # Script chạy riêng Service 1 (Cổng 8000)
├── run_product_service.bat             # Script chạy riêng Service 2 (Cổng 8001)
├── run_order_service.bat               # Script chạy riêng Service 3 (Cổng 8002)
├── run_report_service.bat              # Script chạy riêng Service 4 (Cổng 8003)
├── run_tests.bat                       # Script chạy 70 bài test của cả 4 services
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

### Bước 3: Đồng bộ Cơ sở dữ liệu (Migration) cho cả 4 Services

Khởi tạo và cập nhật cấu trúc database riêng cho từng service:
```bash
# 1. Đồng bộ bảng User cho Auth Service
python manage.py makemigrations
python manage.py migrate

# 2. Đồng bộ bảng products cho Product Service (Kiến trúc SOA)
python product_service/manage.py makemigrations
python product_service/manage.py migrate

# 3. Đồng bộ bảng orders và order_items cho Order Service (Kiến trúc SOA)
python order_service/manage.py makemigrations
python order_service/manage.py migrate

# 4. Đồng bộ bảng orders_reports và product_reports cho Reporting Service (Kiến trúc SOA)
python report_service/manage.py makemigrations
python report_service/manage.py migrate
```

---

### Bước 4: Nạp dữ liệu mẫu để kiểm thử (Seed Data)

Dự án tích hợp sẵn 4 câu lệnh tạo nhanh tài khoản, danh mục sản phẩm, đơn hàng và báo cáo mẫu:

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

3. **Tạo 4 đơn hàng và 6 mặt hàng mẫu (Order Service):**
   ```bash
   python order_service/manage.py seed_orders
   ```
   - Tự động nạp các đơn hàng mẫu kèm chi tiết mặt hàng theo trạng thái `pending`, `completed`, `cancelled`.

4. **Tạo dữ liệu báo cáo thống kê mẫu (Reporting Service):**
   ```bash
   python report_service/manage.py seed_reports
   ```
   - Tự động nạp các bản ghi báo cáo doanh thu, chi phí và lợi nhuận mẫu.

---

### Bước 5: Khởi động hệ thống (Chạy cả 4 Services)

Bạn có thể lựa chọn 1 trong 2 cách sau:

- **Cách 1 (Nhanh nhất - Khuyên dùng trên Windows):**
  Nhấp đúp chuột vào tệp script:
  ```cmd
  run_all_services.bat
  ```
  Script sẽ tự động mở 4 cửa sổ terminal độc lập:
  - Cửa sổ 1: Auth Service tại `http://localhost:8000` (Swagger: `http://localhost:8000/swagger/`)
  - Cửa sổ 2: Product Service tại `http://localhost:8001` (Swagger: `http://localhost:8001/swagger/`)
  - Cửa sổ 3: Order Service tại `http://localhost:8002` (Swagger: `http://localhost:8002/swagger/`)
  - Cửa sổ 4: Reporting Service tại `http://localhost:8003` (Swagger: `http://localhost:8003/swagger/`)

- **Cách 2: Khởi động thủ công qua lệnh Terminal riêng biệt:**
  - **Terminal 1 (Auth Service - Cổng 8000):**
    ```bash
    python manage.py runserver 8000
    ```
  - **Terminal 2 (Product Service - Cổng 8001):**
    ```bash
    python product_service/manage.py runserver 8001
    ```
  - **Terminal 3 (Order Service - Cổng 8002):**
    ```bash
    python order_service/manage.py runserver 8002
    ```
  - **Terminal 4 (Reporting Service - Cổng 8003):**
    ```bash
    python report_service/manage.py runserver 8003
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

#### C. DỊCH VỤ 3: ORDER MANAGEMENT SERVICE (`http://localhost:8002`)
| Chức năng | Phương thức | Đường dẫn (URL) | Mô tả tóm tắt | Quyền truy cập |
| :--- | :---: | :--- | :--- | :---: |
| **Thông tin Service** | `GET` | `/` | Trạng thái và danh mục API Order | Public |
| **Danh sách đơn hàng** | `GET` | `/orders` | Lấy danh sách đơn hàng (`?status=`, `?search=`) |  **Cần Bearer Token (Auth Service)** |
| **Tạo mới đơn hàng** | `POST` | `/orders` | Tạo đơn hàng mới (kiểm tra tồn kho Product Service) |  **Cần Bearer Token (Auth Service)** |
| **Chi tiết đơn hàng** | `GET` | `/orders/<id>` | Xem chi tiết đơn hàng kèm danh sách items |  **Cần Bearer Token (Auth Service)** |
| **Cập nhật trạng thái**| `PUT` / `PATCH`| `/orders/<id>` | Cập nhật trạng thái (hoàn tồn kho nếu cancelled) |  **Cần Bearer Token (Auth Service)** |
| **Xóa đơn hàng** | `DELETE` | `/orders/<id>` | Xóa đơn hàng và tự động hoàn trả tồn kho |  **Cần Bearer Token (Auth Service)** |
| **Danh sách mặt hàng** | `GET` | `/order_items` | Lấy tất cả mặt hàng (hỗ trợ `?order_id=`) |  **Cần Bearer Token (Auth Service)** |
| **Thêm mặt hàng vào đơn** | `POST` | `/order_items` | Thêm mặt hàng (kiểm tra & trừ tồn kho Product Service) |  **Cần Bearer Token (Auth Service)** |
| **Chi tiết mặt hàng** | `GET` | `/order_items/<id>`| Xem thông tin chi tiết một mặt hàng |  **Cần Bearer Token (Auth Service)** |
| **Cập nhật mặt hàng** | `PUT` / `PATCH`| `/order_items/<id>`| Sửa số lượng/giá (tự điều chỉnh tồn kho & tổng tiền) |  **Cần Bearer Token (Auth Service)** |
| **Xóa mặt hàng** | `DELETE` | `/order_items/<id>`| Xóa mặt hàng khỏi đơn (tự hoàn trả tồn kho SP) |  **Cần Bearer Token (Auth Service)** |
| **Swagger UI** | `GET` | `/swagger/` hoặc `/docs/` | Giao diện tài liệu Swagger Service 3 | Public |
| **OpenAPI Schema** | `GET` | `/api/schema/` | Tải về cấu hình OpenAPI Service 3 | Public |
| **Django Admin** | `GET` | `/admin/` | Trang quản trị dữ liệu Orders | Cần Superuser |

#### D. DỊCH VỤ 4: REPORTING SERVICE (`http://localhost:8003`)
| Chức năng | Phương thức | Đường dẫn (URL) | Mô tả tóm tắt | Quyền truy cập |
| :--- | :---: | :--- | :--- | :---: |
| **Thông tin Service** | `GET` | `/` | Trạng thái và danh mục API Báo cáo | Public |
| **Danh sách báo cáo đơn hàng** | `GET` | `/reports/orders` | Lấy tất cả báo cáo đơn hàng (`?order_id=`) |  **Cần Bearer Token (Auth Service)** |
| **Tạo báo cáo đơn hàng** | `POST` | `/reports/orders` | Tạo báo cáo đơn hàng (lấy dữ liệu từ Order Service) |  **Cần Bearer Token (Auth Service)** |
| **Chi tiết báo cáo đơn hàng** | `GET` | `/reports/orders/<id>` | Xem chi tiết báo cáo đơn hàng kèm sản phẩm con |  **Cần Bearer Token (Auth Service)** |
| **Xóa báo cáo đơn hàng** | `DELETE` | `/reports/orders/<id>` | Xóa báo cáo đơn hàng (cascade xóa báo cáo con) |  **Cần Bearer Token (Auth Service)** |
| **Danh sách báo cáo sản phẩm** | `GET` | `/reports/products` | Lấy tất cả báo cáo sản phẩm (`?product_id=`) |  **Cần Bearer Token (Auth Service)** |
| **Tạo báo cáo sản phẩm** | `POST` | `/reports/products` | Tạo báo cáo SP (dữ liệu từ Product/Order Service) |  **Cần Bearer Token (Auth Service)** |
| **Chi tiết báo cáo sản phẩm** | `GET` | `/reports/products/<id>` | Xem chi tiết báo cáo của một sản phẩm |  **Cần Bearer Token (Auth Service)** |
| **Xóa báo cáo sản phẩm** | `DELETE` | `/reports/products/<id>` | Xóa báo cáo sản phẩm khỏi database |  **Cần Bearer Token (Auth Service)** |
| **Swagger UI** | `GET` | `/swagger/` hoặc `/docs/` | Giao diện tài liệu Swagger Service 4 | Public |
| **OpenAPI Schema** | `GET` | `/api/schema/` | Tải về cấu hình OpenAPI Service 4 | Public |
| **Django Admin** | `GET` | `/admin/` | Trang quản trị dữ liệu Báo cáo | Cần Superuser |

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

#### 8.10. API Tạo Đơn hàng mới (POST /orders - Kiểm tra tồn kho liên dịch vụ)
- **Phương thức:** `POST`
- **Đường dẫn:** `http://localhost:8002/orders`
- **Yêu cầu:** Header `Authorization: Bearer <token>`
- **Nghiệp vụ:** Order Service tự động liên lạc sang Product Service tại `http://127.0.0.1:8001/products/<id>` để kiểm tra số lượng tồn kho và tự động trừ tồn kho khi tạo đơn thành công.
- **Body JSON mẫu:**
  ```json
  {
    "customer_name": "Nguyễn Văn An",
    "customer_email": "an.nguyen@example.com",
    "status": "pending",
    "items": [
      {
        "product_id": 1,
        "quantity": 1
      },
      {
        "product_id": 3,
        "quantity": 2
      }
    ]
  }
  ```
- **Phản hồi thành công (`201 Created`):**
  ```json
  {
    "message": "Tạo đơn hàng thành công.",
    "data": {
      "id": 5,
      "customer_name": "Nguyễn Văn An",
      "customer_email": "an.nguyen@example.com",
      "total_amount": "47080000.00",
      "status": "pending",
      "created_at": "2026-11-09T21:50:00Z",
      "updated_at": "2026-11-09T21:50:00Z",
      "items": [
        {
          "id": 7,
          "order_id": 5,
          "product_id": 1,
          "product_name": "Laptop Dell XPS 15 9530",
          "quantity": 1,
          "unit_price": "42500000.00",
          "total_price": "42500000.00"
        },
        {
          "id": 8,
          "order_id": 5,
          "product_id": 3,
          "product_name": "Chuột không dây Logitech MX Master 3S",
          "quantity": 2,
          "unit_price": "2290000.00",
          "total_price": "4580000.00"
        }
      ]
    }
  }
  ```

---

#### 8.11. API Chi tiết & Cập nhật Trạng thái Đơn hàng (GET /orders/:id, PUT /orders/:id)
- **Phương thức:** `GET` (Chi tiết), `PUT` / `PATCH` (Cập nhật trạng thái)
- **Đường dẫn:** `http://localhost:8002/orders/1`
- **Yêu cầu:** Header `Authorization: Bearer <token>`
- **Body JSON Cập nhật Trạng thái sang Cancelled (Hủy đơn hàng):**
  ```json
  {
    "status": "cancelled"
  }
  ```
  *(Khi đơn hàng chuyển sang `cancelled`, Order Service sẽ tự động hoàn trả số lượng tồn kho các mặt hàng về Product Service).*

---

#### 8.12. API Quản lý Mặt hàng trong Đơn hàng (CRUD /order_items)
- **GET /order_items?order_id=1**: Lấy danh sách mặt hàng của đơn hàng #1.
- **POST /order_items**: Thêm một mặt hàng mới vào đơn hàng (tự động kiểm tra và trừ tồn kho SP, đồng thời tính lại `total_amount` của đơn hàng).
- **PUT /order_items/:id**: Điều chỉnh số lượng mặt hàng (tự động bù trừ tồn kho trên Product Service).
- **DELETE /order_items/:id**: Xóa mặt hàng khỏi đơn hàng (hoàn lại tồn kho và cập nhật lại tổng tiền đơn hàng).

---

#### 8.13. API Báo cáo & Thống kê (Reporting Service - Cổng 8003)
- **POST /reports/orders**: Tạo báo cáo theo đơn hàng mới (tự động liên lạc Order Service :8002 để lấy doanh thu `total_revenue`, tự động tính giá vốn và lợi nhuận `total_profit = total_revenue - total_cost`, đồng thời sinh ra các `product_reports` chi tiết).
- **GET /reports/orders**: Lấy danh sách toàn bộ báo cáo đơn hàng (hỗ trợ `?order_id=`).
- **GET /reports/orders/:id**: Xem chi tiết báo cáo đơn hàng kèm các mặt hàng con.
- **DELETE /reports/orders/:id**: Xóa báo cáo đơn hàng (cascade xóa các báo cáo sản phẩm con).
- **POST /reports/products**: Tạo báo cáo theo sản phẩm mới (dữ liệu tích hợp từ Product Service :8001 và Order Service :8002).
- **GET /reports/products**: Lấy danh sách tất cả các báo cáo theo sản phẩm (hỗ trợ `?product_id=`).
- **GET /reports/products/:id**: Xem chi tiết báo cáo của một sản phẩm.
- **DELETE /reports/products/:id**: Xóa một báo cáo sản phẩm khỏi cơ sở dữ liệu.

---

## 9. HƯỚNG DẪN KIỂM THỬ VỚI POSTMAN & SWAGGER UI

### 9.1. Kiểm thử trực quan trên Swagger UI

Hệ thống cung cấp **4 giao diện Swagger UI riêng biệt** cho 4 dịch vụ độc lập:
1. **Auth Service Swagger:** `http://localhost:8000/swagger/`
2. **Product Service Swagger:** `http://localhost:8001/swagger/`
3. **Order Service Swagger:** `http://localhost:8002/swagger/`
4. **Reporting Service Swagger:** `http://localhost:8003/swagger/`

#### Các bước thực hiện:
1. Truy cập Swagger của Auth Service tại `http://localhost:8000/swagger/`.
2. Mở endpoint `POST /` (Login), nhấn **Try it out**, nhập tài khoản `testuser` và mật khẩu `MTIzNDU2`, bấm **Execute** và sao chép mã `token` được trả về.
3. Mở Swagger của bất kỳ service nào (Product :8001, Order :8002, hoặc Reporting :8003).
4. Bấm vào nút **Authorize 🔓** ở góc phải trên cùng của trang:
   - Dán chuỗi `token` vừa sao chép vào ô Value.
   - Nhấn **Authorize** rồi nhấn **Close**.
5. Bây giờ bạn có thể trải nghiệm toàn bộ các thao tác:
   - Sản phẩm: `GET /products`, `POST /products`, v.v.
   - Đơn hàng: `GET /orders`, `POST /orders`, `GET /order_items`, v.v.
   - Báo cáo: `POST /reports/orders`, `GET /reports/products`, v.v.
6. Thử bấm **Logout** trong nút Authorize và gọi lại một API bất kỳ để quan sát hệ thống từ chối với mã lỗi `401 Unauthorized`!

---

### 9.2. Kiểm thử luồng SOA hoàn chỉnh trên Postman
1. **Bước 1 (Auth):** Gửi `POST http://localhost:8000/login` lấy token JWT.
2. **Bước 2 (Product Service):** Gọi `GET http://localhost:8001/products` kiểm tra tồn kho.
3. **Bước 3 (Order Service):** Gửi `POST http://localhost:8002/orders` tạo đơn hàng.
4. **Bước 4 (Reporting Service):** Gửi `POST http://localhost:8003/reports/orders` với `{"order_id": 1}` để sinh báo cáo doanh thu, chi phí và lợi nhuận tự động.

---

## 10. KIỂM THỬ TỰ ĐỘNG (AUTOMATED UNIT TESTS)

Dự án trang bị bộ kiểm thử tự động toàn diện với **tổng cộng 70 bài test độc lập**:
- **Service 1 (Auth Service):** 9 bài test tại [core/tests.py](file:///d:/CODES/Py/Django_Learning/core/tests.py)
- **Service 2 (Product Service):** 17 bài test tại [product_service/products/tests.py](file:///d:/CODES/Py/Django_Learning/product_service/products/tests.py)
- **Service 3 (Order Service):** 23 bài test tại [order_service/orders/tests.py](file:///d:/CODES/Py/Django_Learning/order_service/orders/tests.py)
- **Service 4 (Reporting Service):** 21 bài test tại [report_service/reports/tests.py](file:///d:/CODES/Py/Django_Learning/report_service/reports/tests.py)

### Chạy toàn bộ 70 tests chỉ với 1 thao tác:
- **Trên Windows:** Nhấp đúp vào tệp script:
  ```cmd
  run_tests.bat
  ```
- **Hoặc chạy qua dòng lệnh:**
  ```powershell
  python manage.py test core
  python product_service/manage.py test products
  python order_service/manage.py test orders
  python report_service/manage.py test reports
  ```

### Kết quả chạy kiểm thử thực tế (100% Passed):
```text
========================================================
  CHAY TOAN BO UNIT TESTS CHO CA 4 SERVICES (SOA)
========================================================

[1/4] Kiem thu Service 1 (Auth Service)...
Ran 9 tests in 3.426s
OK

[2/4] Kiem thu Service 2 (Product Service)...
Ran 17 tests in 0.193s
OK

[3/4] Kiem thu Service 3 (Order Service)...
Ran 23 tests in 0.591s
OK

[4/4] Kiem thu Service 4 (Reporting Service)...
Ran 21 tests in 0.236s
OK

========================================================
  [THANH CONG] TAT CA CAC BAI KIEM THU DA VUOT QUA (OK)
========================================================
```

### Danh mục 21 bài test của Service 4 (Reporting Service):
1. `test_get_order_reports_without_token_returns_401`: Chặn 401 khi xem báo cáo đơn không kèm token.
2. `test_get_product_reports_without_token_returns_401`: Chặn 401 khi xem báo cáo sản phẩm không kèm token.
3. `test_get_order_reports_with_invalid_token_returns_401`: Chặn 401 khi token sai lệch hoặc giả mạo.
4. `test_offline_fallback_jwt_verification`: Tự động giải mã JWT dự phòng nội bộ khi Auth Service offline.
5. `test_get_all_order_reports_success`: Lấy danh sách báo cáo đơn hàng thành công (200 OK).
6. `test_get_order_reports_filter_by_order_id`: Lọc danh sách báo cáo đơn hàng theo `order_id`.
7. `test_get_order_report_detail_success`: Lấy chi tiết báo cáo đơn hàng kèm sản phẩm con.
8. `test_get_order_report_detail_not_found`: Trả về 404 khi ID báo cáo đơn không tồn tại.
9. `test_create_order_report_success`: Tạo báo cáo đơn hàng tự động từ dữ liệu Order Service :8002.
10. `test_create_order_report_with_custom_cost`: Tạo báo cáo đơn hàng với chi phí vốn tùy chọn.
11. `test_create_order_report_order_not_found`: Trả về lỗi khi đơn hàng không tồn tại trên Order Service.
12. `test_delete_order_report_success`: Xóa báo cáo đơn hàng và cascade xóa các báo cáo con.
13. `test_get_all_product_reports_success`: Lấy danh sách tất cả các báo cáo theo sản phẩm.
14. `test_get_product_reports_filter_by_product_id`: Lọc danh sách báo cáo theo `product_id`.
15. `test_get_product_report_detail_success`: Lấy chi tiết báo cáo sản phẩm theo ID.
16. `test_get_product_report_detail_not_found`: Trả về 404 khi ID báo cáo sản phẩm không tồn tại.
17. `test_create_product_report_success`: Tạo báo cáo sản phẩm mới thành công.
18. `test_create_product_report_auto_cost`: Tự động tính giá vốn 70% khi không truyền chi phí.
19. `test_delete_product_report_success`: Xóa báo cáo sản phẩm thành công.
20. `test_order_report_model_calculate_profit`: Kiểm thử công thức `total_profit = total_revenue - total_cost`.
21. `test_product_report_model_calculate_profit`: Kiểm thử công thức `profit = revenue - cost`.

---

## 11. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

### 1. Lỗi PowerShell không cho kích hoạt `venv` (`running scripts is disabled on this system`)
- **Nguyên nhân:** Chính sách bảo mật ExecutionPolicy của Windows hạn chế chạy script `.ps1`.
- **Cách khắc phục:** Mở PowerShell và chạy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  .\venv\Scripts\Activate.ps1
  ```

### 2. Gọi API luôn nhận thông báo lỗi 401 Unauthorized
- **Nguyên nhân:** Bạn chưa truyền Header `Authorization` hoặc chưa thêm tiền tố `Bearer ` trước chuỗi token.
- **Cách khắc phục:** Đảm bảo Header có định dạng chính xác:
  ```text
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
  ```
  *(Chú ý có dấu cách giữa từ `Bearer` và chuỗi token)*.

### 3. Cổng bị xung đột hoặc đang được tiến trình khác sử dụng
- **Cách khắc phục:** Khởi chạy máy chủ trên cổng khác:
  - Auth Service: mặc định 8000
  - Product Service: mặc định 8001
  - Order Service: mặc định 8002
  - Reporting Service: mặc định 8003

---

## 👨‍💻 THÔNG TIN DỰ ÁN & TÁC GIẢ

- **Đơn vị đào tạo:** Bộ môn Mạng máy tính & Truyền thông / Kỹ thuật Phần mềm
- **Môn học:** Phát triển Ứng dụng Phân tán & Web Services (RESTful API)
- **Tài liệu tham chiếu:** [BÀI THỰC HÀNH SỐ 1.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%201.pdf), [BÀI THỰC HÀNH SỐ 2.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%202.pdf), [BÀI THỰC HÀNH SỐ 3.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%203.pdf), [BÀI THỰC HÀNH SỐ 4.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%204.pdf) và [BÀI THỰC HÀNH SỐ 5.pdf](file:///d:/CODES/Py/Django_Learning/docs/B%C3%80I%20TH%E1%BB%B0C%20H%C3%80NH%20S%E1%BB%90%205.pdf)
