import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
import jwt
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from reports.models import OrderReport, ProductReport
from reports.service_clients import OrderServiceClient, ProductServiceClient


class ReportingServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Tạo sẵn báo cáo đơn hàng và sản phẩm mẫu
        self.sample_order_report = OrderReport.objects.create(
            order_id=1,
            total_revenue=Decimal("10000000.00"),
            total_cost=Decimal("7000000.00"),
        )
        self.sample_product_report = ProductReport.objects.create(
            order_report=self.sample_order_report,
            product_id=1,
            total_sold=2,
            revenue=Decimal("10000000.00"),
            cost=Decimal("7000000.00"),
        )

        # Tạo JWT token hợp lệ
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'id': 1,
            'username': 'test_admin_user',
            'exp': now + datetime.timedelta(hours=2),
            'iat': now,
        }
        self.valid_token = jwt.encode(payload, settings.AUTH_SECRET_KEY, algorithm='HS256')
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.valid_token}'}

        # Mock Auth Service HTTP POST
        self.auth_patcher = patch('reports.authentication.requests.post')
        self.mock_auth_post = self.auth_patcher.start()
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 200
        mock_auth_resp.json.return_value = {
            "valid": True,
            "user": {"IdUser": 1, "UserName": "test_admin_user"},
            "payload": payload
        }
        self.mock_auth_post.return_value = mock_auth_resp
        self.addCleanup(self.auth_patcher.stop)

        # Mock OrderServiceClient.get_order
        self.patch_get_order = patch.object(
            OrderServiceClient,
            'get_order',
            return_value=(
                {
                    'id': 10,
                    'customer_name': 'Nguyen Van Test',
                    'total_amount': '20000000.00',
                    'status': 'completed',
                    'items': [
                        {
                            'product_id': 1,
                            'product_name': 'Laptop Dell XPS 15',
                            'quantity': 1,
                            'unit_price': '20000000.00',
                            'total_price': '20000000.00'
                        }
                    ]
                },
                None
            )
        ).start()
        self.addCleanup(self.patch_get_order.stop)

        # Mock ProductServiceClient.get_product
        self.patch_get_product = patch.object(
            ProductServiceClient,
            'get_product',
            return_value=({'id': 1, 'name': 'Laptop Dell XPS', 'price': 20000000}, None)
        ).start()
        self.addCleanup(self.patch_get_product.stop)

    # ==========================================
    # 1. KIỂM THỬ XÁC THỰC (AUTHENTICATION TESTS)
    # ==========================================

    def test_get_order_reports_without_token_returns_401(self):
        """Yêu cầu /reports/orders không kèm token phải bị từ chối 401 Unauthorized."""
        response = self.client.get('/reports/orders')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_product_reports_without_token_returns_401(self):
        """Yêu cầu /reports/products không kèm token phải bị từ chối 401 Unauthorized."""
        response = self.client.get('/reports/products')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_reports_with_invalid_token_returns_401(self):
        """Token giả mạo hoặc không hợp lệ phải bị từ chối 401."""
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 401
        mock_auth_resp.json.return_value = {"valid": False, "detail": "Token không hợp lệ."}
        self.mock_auth_post.return_value = mock_auth_resp

        response = self.client.get(
            '/reports/orders',
            HTTP_AUTHORIZATION='Bearer token_sai_hoan_toan_123'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offline_fallback_jwt_verification(self):
        """Khi Auth Service ngoại tuyến, tự động fallback giải mã token nội bộ."""
        import requests
        self.mock_auth_post.side_effect = requests.RequestException("Auth Service unreachable")

        response = self.client.get('/reports/orders', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ==========================================
    # 2. KIỂM THỬ CRUD BÁO CÁO ĐƠN HÀNG (ORDERS REPORTS)
    # ==========================================

    def test_get_all_order_reports_success(self):
        """Lấy danh sách tất cả các báo cáo theo đơn hàng."""
        response = self.client.get('/reports/orders', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(data['total'], 1)

    def test_get_order_reports_filter_by_order_id(self):
        """Lọc báo cáo đơn hàng theo order_id."""
        response = self.client.get(f'/reports/orders?order_id={self.sample_order_report.order_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['data'][0]['order_id'], self.sample_order_report.order_id)

    def test_get_order_report_detail_success(self):
        """Lấy chi tiết báo cáo đơn hàng theo ID kèm danh sách sản phẩm."""
        response = self.client.get(f'/reports/orders/{self.sample_order_report.id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()['data']
        self.assertEqual(data['id'], self.sample_order_report.id)
        self.assertEqual(Decimal(data['total_profit']), Decimal("3000000.00"))
        self.assertEqual(len(data['product_reports']), 1)

    def test_get_order_report_detail_not_found(self):
        """Lấy chi tiết báo cáo đơn hàng không tồn tại trả về 404."""
        response = self.client.get('/reports/orders/99999', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_report_success(self):
        """Tạo báo cáo đơn hàng mới tự động lấy dữ liệu từ Order Service."""
        payload = {"order_id": 10}
        response = self.client.post('/reports/orders', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()['data']
        self.assertEqual(data['order_id'], 10)
        self.assertEqual(Decimal(data['total_revenue']), Decimal("20000000.00"))
        # Tự động tính 70% giá vốn: 14,000,000; lợi nhuận: 6,000,000
        self.assertEqual(Decimal(data['total_cost']), Decimal("14000000.00"))
        self.assertEqual(Decimal(data['total_profit']), Decimal("6000000.00"))
        self.assertEqual(len(data['product_reports']), 1)

    def test_create_order_report_with_custom_cost(self):
        """Tạo báo cáo đơn hàng với chi phí nhập chỉ định riêng."""
        payload = {
            "order_id": 10,
            "total_cost": "15000000.00"
        }
        response = self.client.post('/reports/orders', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()['data']
        self.assertEqual(Decimal(data['total_cost']), Decimal("15000000.00"))
        self.assertEqual(Decimal(data['total_profit']), Decimal("5000000.00"))

    def test_create_order_report_order_not_found(self):
        """Tạo báo cáo cho đơn hàng không tồn tại trên Order Service trả về lỗi."""
        self.patch_get_order.return_value = (None, "Không tìm thấy đơn hàng với ID 99 trên Order Service.")
        payload = {"order_id": 99}
        response = self.client.post('/reports/orders', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_report_success(self):
        """Xóa báo cáo đơn hàng thành công và cascade xóa product_reports con."""
        rep_id = self.sample_order_report.id
        prod_rep_id = self.sample_product_report.id
        response = self.client.delete(f'/reports/orders/{rep_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(OrderReport.objects.filter(pk=rep_id).exists())
        self.assertFalse(ProductReport.objects.filter(pk=prod_rep_id).exists())

    # ==========================================
    # 3. KIỂM THỬ CRUD BÁO CÁO SẢN PHẨM (PRODUCT REPORTS)
    # ==========================================

    def test_get_all_product_reports_success(self):
        """Lấy danh sách tất cả các báo cáo theo sản phẩm."""
        response = self.client.get('/reports/products', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(data['total'], 1)

    def test_get_product_reports_filter_by_product_id(self):
        """Lọc danh sách báo cáo sản phẩm theo product_id."""
        response = self.client.get(f'/reports/products?product_id={self.sample_product_report.product_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['data'][0]['product_id'], self.sample_product_report.product_id)

    def test_get_product_report_detail_success(self):
        """Lấy chi tiết báo cáo sản phẩm theo ID."""
        response = self.client.get(f'/reports/products/{self.sample_product_report.id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()['data']
        self.assertEqual(data['id'], self.sample_product_report.id)
        self.assertEqual(Decimal(data['profit']), Decimal("3000000.00"))

    def test_get_product_report_detail_not_found(self):
        """Lấy chi tiết báo cáo sản phẩm không tồn tại trả về 404."""
        response = self.client.get('/reports/products/99999', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product_report_success(self):
        """Tạo báo cáo sản phẩm mới thành công với doanh thu và chi phí tùy chọn."""
        payload = {
            "product_id": 2,
            "total_sold": 3,
            "revenue": "15000000.00",
            "cost": "10000000.00"
        }
        response = self.client.post('/reports/products', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()['data']
        self.assertEqual(data['product_id'], 2)
        self.assertEqual(Decimal(data['profit']), Decimal("5000000.00"))

    def test_create_product_report_auto_cost(self):
        """Tạo báo cáo sản phẩm tự động tính chi phí vốn 70%."""
        payload = {
            "product_id": 3,
            "total_sold": 1,
            "revenue": "1000000.00"
        }
        response = self.client.post('/reports/products', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()['data']
        self.assertEqual(Decimal(data['cost']), Decimal("700000.00"))
        self.assertEqual(Decimal(data['profit']), Decimal("300000.00"))

    def test_delete_product_report_success(self):
        """Xóa một báo cáo sản phẩm thành công."""
        rep_id = self.sample_product_report.id
        response = self.client.delete(f'/reports/products/{rep_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ProductReport.objects.filter(pk=rep_id).exists())

    # ==========================================
    # 4. KIỂM THỬ TÍNH TOÁN LỢI NHUẬN (PROFIT CALCULATION)
    # ==========================================

    def test_order_report_model_calculate_profit(self):
        """Kiểm tra logic tính lợi nhuận trên OrderReport model."""
        report = OrderReport(
            order_id=5,
            total_revenue=Decimal("5000000.00"),
            total_cost=Decimal("3500000.00")
        )
        report.save()
        self.assertEqual(report.total_profit, Decimal("1500000.00"))

    def test_product_report_model_calculate_profit(self):
        """Kiểm tra logic tính lợi nhuận trên ProductReport model."""
        report = ProductReport(
            product_id=5,
            total_sold=1,
            revenue=Decimal("2000000.00"),
            cost=Decimal("1200000.00")
        )
        report.save()
        self.assertEqual(report.profit, Decimal("800000.00"))

