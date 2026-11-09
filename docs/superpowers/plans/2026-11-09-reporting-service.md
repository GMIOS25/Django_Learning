# Reporting Service (Bài Thực Hành Số 5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng hoàn chỉnh Dịch vụ Báo cáo (Reporting Service - Bài Thực Hành Số 5) theo kiến trúc hướng dịch vụ (SOA) chạy độc lập trên cổng 8003 và cơ sở dữ liệu riêng SQLite `reports_db.sqlite3`, liên kết dữ liệu với Auth Service (8000), Product Service (8001), và Order Service (8002).

**Architecture:** 
- Kiến trúc SOA gồm 4 dịch vụ độc lập: Auth Service (Port 8000), Product Service (Port 8001), Order Service (Port 8002), Reporting Service (Port 8003).
- Reporting Service giao tiếp REST HTTP tới Auth Service để thẩm định token JWT, tới Order Service để lấy dữ liệu đơn hàng và chi tiết mặt hàng, và tới Product Service để lấy thông tin sản phẩm và tồn kho.
- Lưu trữ 2 bảng CSDL quan hệ theo Phụ lục: `orders_reports` và `product_reports`. Tự động tính toán các trường doanh thu (`revenue`), chi phí (`cost`), lợi nhuận (`profit = revenue - cost`).

**Tech Stack:** Python 3.12, Django 5.x, Django REST Framework 3.15+, PyJWT, requests, drf-spectacular (OpenAPI 3.0 / Swagger UI).

**Spec:** [docs/BÀI THỰC HÀNH SỐ 5.pdf](file:///d:/CODES/Py/Django_Learning/docs/BÀI%20THỰC%20HÀNH%20SỐ%205.pdf)

## Global Constraints

- Chạy độc lập trên cổng `8003` với cơ sở dữ liệu riêng `report_service/reports_db.sqlite3`.
- Bảng `orders_reports`: `id`, `order_id`, `total_revenue`, `total_cost`, `total_profit`.
- Bảng `product_reports`: `id`, `order_report_id`, `product_id`, `total_sold`, `revenue`, `cost`, `profit`.
- Xác thực qua Auth Service (Bài 2) qua header `Authorization: Bearer <token>`.
- Các endpoints yêu cầu: `GET /reports/products`, `GET /reports/products/<id>`, `GET /reports/orders`, `GET /reports/orders/<id>`, `POST /reports/products`, `POST /reports/orders`, `DELETE /reports/products/<id>`, `DELETE /reports/orders/<id>`.
- Swagger UI tài liệu API hoạt động tại `http://localhost:8003/swagger/`.

## Review Focus

1. **Xác thực JWT:** Mọi request thiếu hoặc sai token phải bị từ chối với mã `401 Unauthorized`.
2. **Tính toán số học chính xác:** `total_profit = total_revenue - total_cost` và `profit = revenue - cost`, không bị sai lệch số thập phân (sử dụng `Decimal`).
3. **Liên kết dữ liệu liên dịch vụ:** Khi gọi `POST /reports/orders`, dịch vụ kết nối thành công tới Order Service để lấy đúng đơn hàng và các mặt hàng; xử lý trả về 404/400 nếu đơn hàng không tồn tại.
4. **Xóa báo cáo đơn hàng liên đới:** Khi xóa một báo cáo đơn hàng (`DELETE /reports/orders/<id>`), các báo cáo sản phẩm thuộc về báo cáo đơn hàng đó (`CASCADE`) phải được dọn dẹp an toàn.
5. **Dung sai lỗi ngoại tuyến:** Khi Order Service hoặc Product Service không phản hồi, Reporting Service trả về thông báo lỗi HTTP thích hợp thay vì làm crash tiến trình.

---

### Task 1: Khởi tạo cấu trúc dự án Django cho Reporting Service

**Files:**
- Create: `report_service/manage.py`
- Create: `report_service/report_project/__init__.py`
- Create: `report_service/report_project/settings.py`
- Create: `report_service/report_project/urls.py`
- Create: `report_service/report_project/asgi.py`
- Create: `report_service/report_project/wsgi.py`
- Create: `report_service/reports/__init__.py`
- Create: `report_service/reports/apps.py`

**Interfaces:**
- Produces: Dự án Django hoạt động trên cổng 8003, cấu hình database `reports_db.sqlite3`, tích hợp `rest_framework` và `drf_spectacular`.

- [x] **Step 1: Tạo cấu trúc thư mục và các file cấu hình `report_project`**
- [x] **Step 2: Cấu hình `settings.py`** (Database riêng `reports_db.sqlite3`, `AUTH_SERVICE_URL`, `ORDER_SERVICE_URL`, `PRODUCT_SERVICE_URL`, cấu hình Swagger).
- [x] **Step 3: Cấu hình `report_project/urls.py`** với route Swagger và include `reports.urls`.

---

### Task 2: Định nghĩa Models, Migrations và Admin cho Reporting Service

**Files:**
- Create: `report_service/reports/models.py`
- Create: `report_service/reports/admin.py`
- Create: `report_service/reports/migrations/__init__.py`

**Interfaces:**
- Produces: Model `OrderReport` và `ProductReport` theo đúng kiểu dữ liệu Phụ lục Bài 5.

- [x] **Step 1: Viết `report_service/reports/models.py`**
Định nghĩa `OrderReport` (`orders_reports`) và `ProductReport` (`product_reports`) với các phương thức tự động tính `total_profit` và `profit`.
- [x] **Step 2: Viết `report_service/reports/admin.py`**
Đăng ký `OrderReportAdmin` và `ProductReportAdmin` trong Django Admin.
- [x] **Step 3: Chạy makemigrations và migrate**
Tạo file migration và áp dụng vào `report_service/reports_db.sqlite3`.

---

### Task 3: Xây dựng Module Xác thực & Inter-Service Clients

**Files:**
- Create: `report_service/reports/authentication.py`
- Create: `report_service/reports/service_clients.py`

**Interfaces:**
- Consumes: Cấu hình URL từ `settings.py`, thư viện `requests`, `jwt`.
- Produces: `AuthServiceAuthentication`, `IsAuthServiceAuthenticated`, `OrderServiceClient`, `ProductServiceClient`.

- [x] **Step 1: Tạo `authentication.py`**
Thẩm định Bearer token với Auth Service (`http://127.0.0.1:8000/auth`), hỗ trợ fallback JWT nội bộ khi unit test.
- [x] **Step 2: Tạo `service_clients.py`**
Hỗ trợ lấy chi tiết đơn hàng `get_order(order_id)` từ Order Service và lấy thông tin sản phẩm `get_product(product_id)` từ Product Service.

---

### Task 4: Xây dựng Serializers và Controllers (Views & URLs)

**Files:**
- Create: `report_service/reports/serializers.py`
- Create: `report_service/reports/views.py`
- Create: `report_service/reports/urls.py`
- Create: `report_service/reports/management/commands/seed_reports.py`

**Interfaces:**
- Consumes: `OrderReport`, `ProductReport`, `service_clients`, `authentication`.
- Produces:
  - `GET /reports/orders`: Danh sách báo cáo đơn hàng.
  - `GET /reports/orders/<id>`: Chi tiết báo cáo đơn hàng kèm các báo cáo sản phẩm con.
  - `POST /reports/orders`: Tạo báo cáo đơn hàng từ dữ liệu Order Service.
  - `DELETE /reports/orders/<id>`: Xóa báo cáo đơn hàng.
  - `GET /reports/products`: Danh sách báo cáo sản phẩm.
  - `GET /reports/products/<id>`: Chi tiết báo cáo sản phẩm.
  - `POST /reports/products`: Tạo báo cáo sản phẩm dựa trên dữ liệu sản phẩm và đơn hàng.
  - `DELETE /reports/products/<id>`: Xóa báo cáo sản phẩm.

- [x] **Step 1: Viết `serializers.py`** cho OrderReport và ProductReport.
- [x] **Step 2: Viết `views.py`** triển khai đầy đủ các controller với schema OpenAPI decorators.
- [x] **Step 3: Viết `urls.py`** định tuyến đúng chuẩn các đường dẫn `/reports/orders` và `/reports/products`.
- [x] **Step 4: Viết command `seed_reports.py`** khởi tạo dữ liệu mẫu báo cáo.
- [x] **Step 5: Kiểm tra `python report_service/manage.py check`** không có lỗi.

---

### Task 5: Viết bộ Kiểm thử tự động (Unit & Integration Tests)

**Files:**
- Create: `report_service/reports/tests.py`

**Interfaces:**
- Consumes: `APIClient`, `unittest.mock.patch`, models & views của Reporting Service.
- Produces: Bộ test cases toàn diện cho Service 4.

- [x] **Step 1: Viết test xác thực** (401 khi không token, 200 khi có token hợp lệ).
- [x] **Step 2: Viết test CRUD Order Reports** (GET list, GET detail, POST create kết hợp mock OrderServiceClient, DELETE, kiểm tra tính toán lợi nhuận).
- [x] **Step 3: Viết test CRUD Product Reports** (GET list, GET detail, POST create, DELETE).
- [x] **Step 4: Chạy `python report_service/manage.py test reports`** đạt 100% OK.

---

### Task 6: Tích hợp Scripts hệ thống và Cập nhật Báo cáo README.md

**Files:**
- Create: `run_report_service.bat`
- Modify: `run_all_services.bat`
- Modify: `run_tests.bat`
- Modify: `README.md`

- [x] **Step 1: Tạo `run_report_service.bat`** (Khởi chạy trên cổng 8003).
- [x] **Step 2: Cập nhật `run_all_services.bat`** (Khởi chạy đồng thời cả 4 services).
- [x] **Step 3: Cập nhật `run_tests.bat`** (Chạy kiểm thử tự động cho cả 4 services).
- [x] **Step 4: Cập nhật tài liệu `README.md`** bao gồm Bài Thực Hành Số 5.
- [x] **Step 5: Chạy toàn bộ test hệ thống qua `run_tests.bat`** để chứng thực kết quả (Evidence Before Claims).
