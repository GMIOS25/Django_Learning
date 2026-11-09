import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
import jwt
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from orders.product_client import ProductServiceClient


class OrderServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Tạo sẵn đơn hàng mẫu và mặt hàng mẫu
        self.sample_order = Order.objects.create(
            customer_name="Nguyen Van A",
            customer_email="a.nguyen@example.com",
            status=Order.STATUS_PENDING,
        )
        self.sample_item = OrderItem.objects.create(
            order=self.sample_order,
            product_id=1,
            product_name="Laptop Dell XPS 15",
            quantity=1,
            unit_price=Decimal("42500000.00"),
        )
        self.sample_order.recalculate_total()

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
        self.auth_patcher = patch('orders.authentication.requests.post')
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

        # Mock ProductServiceClient calls
        self.patch_check_stock = patch.object(
            ProductServiceClient,
            'check_stock',
            return_value=(True, {'id': 2, 'name': 'Ban phim co Keychron', 'price': 4850000, 'quantity': 10}, None)
        ).start()
        self.addCleanup(self.patch_check_stock.stop)

        self.patch_deduct_stock = patch.object(
            ProductServiceClient,
            'deduct_stock',
            return_value=(True, None)
        ).start()
        self.addCleanup(self.patch_deduct_stock.stop)

        self.patch_restore_stock = patch.object(
            ProductServiceClient,
            'restore_stock',
            return_value=(True, None)
        ).start()
        self.addCleanup(self.patch_restore_stock.stop)

    # ==========================================
    # 1. KIỂM THỬ XÁC THỰC (AUTHENTICATION TESTS)
    # ==========================================

    def test_get_orders_without_token_returns_401(self):
        """Yêu cầu /orders không kèm token phải bị từ chối 401 Unauthorized."""
        response = self.client.get('/orders')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_with_invalid_token_returns_401(self):
        """Token giả mạo hoặc không hợp lệ phải bị từ chối 401."""
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 401
        mock_auth_resp.json.return_value = {"valid": False, "detail": "Token không hợp lệ."}
        self.mock_auth_post.return_value = mock_auth_resp

        response = self.client.get(
            '/orders',
            HTTP_AUTHORIZATION='Bearer token_sai_hoan_toan_123'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_with_expired_token_returns_401(self):
        """Token đã hết hạn phải bị từ chối 401."""
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 401
        mock_auth_resp.json.return_value = {"valid": False, "detail": "Token đã hết hạn."}
        self.mock_auth_post.return_value = mock_auth_resp

        response = self.client.get(
            '/orders',
            HTTP_AUTHORIZATION='Bearer token_het_han_xyz'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offline_fallback_jwt_verification(self):
        """Khi Auth Service ngoại tuyến, tự động fallback giải mã token nội bộ."""
        import requests
        self.mock_auth_post.side_effect = requests.RequestException("Auth Service unreachable")

        response = self.client.get('/orders', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ==========================================
    # 2. KIỂM THỬ CRUD ĐƠN HÀNG (ORDERS API TESTS)
    # ==========================================

    def test_get_all_orders_success(self):
        """Lấy danh sách đơn hàng với token hợp lệ trả về HTTP 200 OK."""
        response = self.client.get('/orders', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('data', data)
        self.assertGreaterEqual(data['total'], 1)

    def test_get_orders_filter_by_status(self):
        """Lọc danh sách đơn hàng theo trạng thái."""
        response = self.client.get('/orders?status=pending', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(all(o['status'] == 'pending' for o in data['data']))

    def test_get_orders_filter_by_search(self):
        """Tìm kiếm đơn hàng theo tên hoặc email khách hàng."""
        response = self.client.get('/orders?search=Nguyen', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(data['total'], 1)

    def test_get_order_detail_success(self):
        """Lấy chi tiết đơn hàng theo ID hợp lệ trả về 200 OK kèm danh sách items."""
        response = self.client.get(f'/orders/{self.sample_order.id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['data']['id'], self.sample_order.id)
        self.assertEqual(len(data['data']['items']), 1)

    def test_get_order_detail_not_found(self):
        """Lấy chi tiết đơn hàng với ID không tồn tại trả về 404."""
        response = self.client.get('/orders/99999', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_success(self):
        """Tạo đơn hàng mới kiểm tra tồn kho và trừ tồn kho thành công."""
        payload = {
            "customer_name": "Tran Thi B",
            "customer_email": "b.tran@example.com",
            "status": "pending",
            "items": [
                {
                    "product_id": 2,
                    "quantity": 2,
                    "product_name": "Ban phim co Keychron",
                    "unit_price": "4850000.00"
                }
            ]
        }
        response = self.client.post('/orders', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['data']['customer_name'], "Tran Thi B")
        self.assertEqual(Decimal(data['data']['total_amount']), Decimal("9700000.00"))

        # Xác nhận có gọi check_stock và deduct_stock
        self.patch_check_stock.assert_called()
        self.patch_deduct_stock.assert_called()

    def test_create_order_insufficient_stock_fails(self):
        """Khi Product Service báo không đủ tồn kho, tạo đơn hàng trả về 400 Bad Request."""
        self.patch_check_stock.return_value = (False, None, "Sản phẩm không đủ tồn kho.")

        payload = {
            "customer_name": "Le Hoang C",
            "customer_email": "c.le@example.com",
            "items": [{"product_id": 99, "quantity": 100}]
        }
        response = self.client.post('/orders', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.json())

    def test_create_order_invalid_data(self):
        """Tạo đơn hàng thiếu tên khách hàng hoặc email sai định dạng trả về 400."""
        payload = {
            "customer_name": "",
            "customer_email": "email_khong_hop_le",
        }
        response = self.client.post('/orders', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_to_completed(self):
        """Cập nhật trạng thái đơn hàng sang completed thành công."""
        payload = {"status": "completed"}
        response = self.client.put(f'/orders/{self.sample_order.id}', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sample_order.refresh_from_db()
        self.assertEqual(self.sample_order.status, "completed")

    def test_update_order_status_to_cancelled_restores_stock(self):
        """Khi chuyển đơn hàng sang trạng thái cancelled, tự động hoàn trả tồn kho."""
        payload = {"status": "cancelled"}
        response = self.client.put(f'/orders/{self.sample_order.id}', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sample_order.refresh_from_db()
        self.assertEqual(self.sample_order.status, "cancelled")
        # Kiểm tra hàm restore_stock đã được gọi cho item của order
        self.patch_restore_stock.assert_called()

    def test_delete_order_success(self):
        """Xóa đơn hàng thành công và tự động hoàn trả tồn kho cho sản phẩm."""
        order_id = self.sample_order.id
        response = self.client.delete(f'/orders/{order_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Order.objects.filter(pk=order_id).exists())
        self.patch_restore_stock.assert_called()

    # ==========================================
    # 3. KIỂM THỬ CRUD CHI TIẾT ĐƠN HÀNG (ORDER ITEMS API)
    # ==========================================

    def test_get_all_order_items(self):
        """Lấy danh sách tất cả các chi tiết đơn hàng trả về 200 OK."""
        response = self.client.get('/order_items', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(data['total'], 1)

    def test_get_order_items_by_order_id(self):
        """Lọc danh sách chi tiết đơn hàng theo order_id."""
        response = self.client.get(f'/order_items?order_id={self.sample_order.id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['data'][0]['order_id'], self.sample_order.id)

    def test_get_order_item_detail_success(self):
        """Lấy chi tiết một mặt hàng theo ID."""
        response = self.client.get(f'/order_items/{self.sample_item.id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['data']['id'], self.sample_item.id)

    def test_get_order_item_detail_not_found(self):
        """Lấy chi tiết một mặt hàng không tồn tại trả về 404."""
        response = self.client.get('/order_items/99999', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_item_success(self):
        """Thêm mặt hàng mới vào đơn hàng và kiểm tra tính lại total_amount."""
        payload = {
            "order_id": self.sample_order.id,
            "product_id": 3,
            "product_name": "Chuot MX Master 3S",
            "quantity": 1,
            "unit_price": "2290000.00"
        }
        response = self.client.post('/order_items', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.sample_order.refresh_from_db()
        expected_total = Decimal("42500000.00") + Decimal("2290000.00")
        self.assertEqual(self.sample_order.total_amount, expected_total)

    def test_create_order_item_insufficient_stock(self):
        """Thêm mặt hàng vào đơn khi thiếu hàng trả về 400 Bad Request."""
        self.patch_check_stock.return_value = (False, None, "Không đủ hàng tồn kho.")
        payload = {
            "order_id": self.sample_order.id,
            "product_id": 99,
            "quantity": 10
        }
        response = self.client.post('/order_items', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_item_quantity(self):
        """Cập nhật số lượng của mặt hàng và tính lại tổng tiền đơn hàng."""
        payload = {"quantity": 2}
        response = self.client.put(f'/order_items/{self.sample_item.id}', data=payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sample_item.refresh_from_db()
        self.assertEqual(self.sample_item.quantity, 2)
        self.sample_order.refresh_from_db()
        self.assertEqual(self.sample_order.total_amount, Decimal("85000000.00"))

    def test_delete_order_item_success(self):
        """Xóa mặt hàng khỏi đơn hàng và tính lại tổng tiền đơn hàng."""
        item_id = self.sample_item.id
        response = self.client.delete(f'/order_items/{item_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(OrderItem.objects.filter(pk=item_id).exists())
        self.sample_order.refresh_from_db()
        self.assertEqual(self.sample_order.total_amount, Decimal("0.00"))

