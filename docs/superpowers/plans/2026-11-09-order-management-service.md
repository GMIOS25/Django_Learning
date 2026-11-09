# Order Management Service (Bài Thực Hành Số 4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện toàn bộ Dịch vụ Quản lý Đơn hàng (Order Management Service - Bài Thực Hành Số 4) theo kiến trúc hướng dịch vụ (SOA) chạy độc lập trên cổng 8002 và cơ sở dữ liệu riêng SQLite, liên lạc xác thực qua Auth Service (8000) và kiểm tra/trừ tồn kho qua Product Service (8001).

**Architecture:** 
- Kiến trúc SOA gồm 3 dịch vụ độc lập: Auth Service (Port 8000), Product Service (Port 8001), Order Service (Port 8002).
- Order Service giao tiếp REST HTTP tới Auth Service qua `AuthServiceAuthentication` để xác thực JWT token và tới Product Service qua `ProductServiceClient` để kiểm tra tồn kho (`check_stock`), trừ tồn kho khi tạo đơn (`deduct_stock`), và hoàn trả tồn kho khi hủy đơn (`restore_stock`).
- Quản lý giao dịch nguyên tử (`transaction.atomic`) bảo toàn tính toàn vẹn dữ liệu giữa `Order` và `OrderItem`.

**Tech Stack:** Python 3.12, Django 5.x, Django REST Framework 3.15+, PyJWT, requests, drf-spectacular (OpenAPI 3.0 / Swagger UI).

**Spec:** [docs/BÀI THỰC HÀNH SỐ 4.pdf](file:///d:/CODES/Py/Django_Learning/docs/BÀI%20THỰC%20HÀNH%20SỐ%204.pdf)

## Global Constraints

- Chạy độc lập trên cổng `8002` với cơ sở dữ liệu riêng `order_service/orders_db.sqlite3`.
- Bảng `orders`: `id`, `customer_name`, `customer_email`, `total_amount`, `status`, `created_at`, `updated_at`.
- Bảng `order_items`: `id`, `order_id`, `product_id`, `product_name`, `quantity`, `unit_price`, `total_price`.
- Phải xác thực qua Auth Service (bài 2) qua header `Authorization: Bearer <token>`.
- Phải kiểm tra tồn kho từ Product Service (bài 3) trước khi tạo đơn hàng.
- Tất cả endpoints hỗ trợ định dạng chuẩn: `GET /orders`, `GET /orders/<id>`, `POST /orders`, `PUT /orders/<id>`, `DELETE /orders/<id>`, `GET /order_items`, `GET /order_items/<id>`, `POST /order_items`, `PUT /order_items/<id>`, `DELETE /order_items/<id>`.

## Review Focus

1. **Token xác thực:** Yêu cầu thiếu hoặc sai token JWT phải bị từ chối với mã `401 Unauthorized`.
2. **Kiểm tra tồn kho không đủ:** Khi `requested_quantity > stock` trên Product Service, trả về `400 Bad Request` và thông báo lỗi rõ ràng.
3. **Cập nhật trạng thái đơn hủy (`cancelled`):** Khi chuyển đơn sang `cancelled` hoặc xóa đơn hàng, hệ thống phải hoàn trả số lượng tồn kho trên Product Service.
4. **Tính toán tổng tiền tự động:** Khi thêm, sửa hoặc xóa `OrderItem`, thuộc tính `total_price` và `total_amount` của đơn hàng phải được tự động tính toán lại chính xác.
5. **Dung sai lỗi khi Product Service ngoại tuyến:** Khi Product Service offline, trả về thông báo lỗi kết nối rõ ràng thay vì làm crash service.

---

### Task 1: Khôi phục Routing URL và Django Admin cho Order Service

**Files:**
- Create: `order_service/orders/urls.py`
- Create: `order_service/orders/admin.py`
- Modify: `order_service/order_project/urls.py`

**Interfaces:**
- Consumes: Models `Order`, `OrderItem` từ `order_service.orders.models`.
- Produces: `urlpatterns` chứa các route: `orders/`, `orders/<pk>/`, `order_items/`, `order_items/<pk>/`.

- [x] **Step 1: Tạo `order_service/orders/urls.py`**
Định nghĩa các URL pattern tương thích với schema Swagger và regex:
```python
from django.urls import re_path
from .views import (
    order_list_create_view,
    order_detail_update_delete_view,
    order_item_list_create_view,
    order_item_detail_update_delete_view,
)

urlpatterns = [
    re_path(r'^orders/?$', order_list_create_view, name='order_list_create'),
    re_path(r'^orders/(?P<pk>\d+)/?$', order_detail_update_delete_view, name='order_detail_update_delete'),
    re_path(r'^order_items/?$', order_item_list_create_view, name='order_item_list_create'),
    re_path(r'^order_items/(?P<pk>\d+)/?$', order_item_detail_update_delete_view, name='order_item_detail_update_delete'),
]
```

- [x] **Step 2: Tạo `order_service/orders/admin.py`**
Đăng ký `OrderAdmin` với `OrderItemInline` và `OrderItemAdmin` vào Django Admin.

- [x] **Step 3: Tạo lệnh seed dữ liệu `order_service/orders/management/commands/seed_orders.py`**
Khôi phục command `seed_orders` để khởi tạo dữ liệu mẫu khi cần.

---

### Task 2: Xây dựng Controller / Views cho Order Service

**Files:**
- Create: `order_service/orders/views.py`

**Interfaces:**
- Consumes: 
  - `Order`, `OrderItem` từ `orders.models`
  - Serializers từ `orders.serializers`
  - `AuthServiceAuthentication`, `IsAuthServiceAuthenticated` từ `orders.authentication`
  - `ProductServiceClient` từ `orders.product_client`
- Produces: 
  - `order_list_create_view`
  - `order_detail_update_delete_view`
  - `order_item_list_create_view`
  - `order_item_detail_update_delete_view`

- [x] **Step 1: Viết `order_list_create_view`**
Xử lý `GET /orders` (hỗ trợ lọc status, search tên/email) và `POST /orders` (kiểm tra tồn kho qua `ProductServiceClient.check_stock`, trừ tồn kho bằng `ProductServiceClient.deduct_stock`, tạo đơn hàng trong `transaction.atomic()`).

- [x] **Step 2: Viết `order_detail_update_delete_view`**
Xử lý `GET /orders/<id>`, `PUT` / `PATCH` (cập nhật trạng thái; nếu sang `cancelled`, tự động hoàn trả tồn kho qua `ProductServiceClient.restore_stock`), và `DELETE /orders/<id>` (xóa đơn và hoàn tồn kho nếu chưa bị hủy).

- [x] **Step 3: Viết `order_item_list_create_view`**
Xử lý `GET /order_items` (lọc theo `order_id`) và `POST /order_items` (kiểm tra tồn kho, trừ tồn kho, thêm item vào đơn hàng, tự động tính lại `total_amount`).

- [x] **Step 4: Viết `order_item_detail_update_delete_view`**
Xử lý `GET /order_items/<id>`, `PUT` / `PATCH` (điều chỉnh số lượng chênh lệch tồn kho), và `DELETE /order_items/<id>` (xóa item, hoàn lại tồn kho, tính lại `total_amount`).

- [x] **Step 5: Kiểm tra cấu hình Django check**
Chạy `.\venv\Scripts\python.exe order_service/manage.py check` xác nhận không còn lỗi import hay syntax.

---

### Task 3: Xây dựng bộ Unit & Integration Tests cho Order Service

**Files:**
- Create: `order_service/orders/tests.py`

**Interfaces:**
- Consumes: Test framework `rest_framework.test.APIClient`, `unittest.mock.patch`, models & views của Order Service.
- Produces: Bộ test cases toàn diện chạy tự động cho Service 3.

- [x] **Step 1: Viết test authentication**
Kiểm tra request không có token trả về `401 Unauthorized`, request có Bearer token hợp lệ được chấp thuận.

- [x] **Step 2: Viết test CRUD Orders**
Kiểm tra `GET /orders`, `GET /orders/<id>`, 404 khi không tồn tại.
Kiểm tra `POST /orders` với mocked `ProductServiceClient`: trường hợp đủ hàng (201 Created), trường hợp thiếu hàng (400 Bad Request).
Kiểm tra `PUT /orders/<id>` cập nhật trạng thái đơn sang `completed` và `cancelled`.
Kiểm tra `DELETE /orders/<id>`.

- [x] **Step 3: Viết test CRUD Order Items**
Kiểm tra `GET /order_items`, `POST /order_items`, `PUT /order_items/<id>`, `DELETE /order_items/<id>`.
Kiểm tra tính toán lại `total_amount` trên `Order` cha sau các thao tác item.

- [x] **Step 4: Chạy test Order Service**
Chạy `.\venv\Scripts\python.exe order_service/manage.py test orders` và đảm bảo tất cả test cases đạt 100% OK.

---

### Task 4: Cập nhật Scripts khởi chạy và Kiểm thử tự động toàn diện

**Files:**
- Create: `run_order_service.bat`
- Modify: `run_all_services.bat`
- Modify: `run_tests.bat`

- [x] **Step 1: Tạo `run_order_service.bat`**
Khởi động Order Service trên cổng `8002`:
```bat
@echo off
echo ========================================================
echo   KHOI DONG ORDER SERVICE (BAI THUC HANH SO 4 - SOA)
echo   Chay tai: http://127.0.0.1:8002
echo ========================================================
cd /d %~dp0
call .\venv\Scripts\activate.bat
python order_service\manage.py runserver 8002
```

- [x] **Step 2: Cập nhật `run_all_services.bat`**
Thêm Service 3 (Order Service - Port 8002) vào kịch bản khởi động đồng thời 3 cửa sổ.

- [x] **Step 3: Cập nhật `run_tests.bat`**
Thêm bước `[3/3] Kiem thu Service 3 (Order Service)...` chạy `python order_service\manage.py test orders`.

- [x] **Step 4: Chạy thử nghiệm script kiểm thử tổng**
Chạy `run_tests.bat` để xác nhận cả 3 services đều vượt qua test.

---

### Task 5: Cập nhật Tài liệu Báo cáo README.md & Đồng bộ Dự án

**Files:**
- Modify: `README.md`

- [x] **Step 1: Cập nhật Header & Mục lục**
Bổ sung Bài Thực Hành Số 4 vào tiêu đề, phần giới thiệu và mục lục.

- [x] **Step 2: Bổ sung Bảng đối soát hoàn thành Bài Thực Hành Số 4**
Liệt kê chi tiết 100% tiêu chí từ file PDF Bài 4 và vị trí code tương ứng.

- [x] **Step 3: Cập nhật Sơ đồ kiến trúc SOA 3 Services**
Minh họa luồng tương tác giữa Client ↔ Auth (8000) ↔ Product (8001) ↔ Order (8002).

- [x] **Step 4: Tài liệu đặc tả API chi tiết cho Order Service**
Hướng dẫn chi tiết tham số, header xác thực và mẫu cURL / Postman cho `/orders` và `/order_items`.
