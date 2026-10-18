import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
import jwt
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Product


class ProductServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Tạo sẵn sản phẩm mẫu trong database riêng của Product Service
        self.sample_product = Product.objects.create(
            name="Laptop Gaming ASUS ROG Zephyrus G14",
            description="Ryzen 9 8945HS, RTX 4060, 32GB RAM, OLED 120Hz.",
            price=Decimal("41990000.00"),
            quantity=12
        )

        # Tạo một JWT token hợp lệ khớp với thuật toán HS256 và AUTH_SECRET_KEY
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'id': 1,
            'username': 'test_admin_user',
            'exp': now + datetime.timedelta(hours=2),
            'iat': now,
        }
        self.valid_token = jwt.encode(payload, settings.AUTH_SECRET_KEY, algorithm='HS256')
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.valid_token}'}

        # Thiết lập mock mặc định cho HTTP call sang Auth Service để bài test chạy siêu nhanh (<1s)
        self.patcher = patch('products.authentication.requests.post')
        self.mock_post = self.patcher.start()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": True,
            "user": {"IdUser": 1, "UserName": "test_admin_user"},
            "payload": payload
        }
        self.mock_post.return_value = mock_response
        self.addCleanup(self.patcher.stop)

    # ==========================================
    # 1. KIỂM THỬ XÁC THỰC (AUTHENTICATION TESTS)
    # ==========================================

    def test_get_products_without_token_returns_401(self):
        """Yêu cầu /products không kèm token phải bị từ chối 401 Unauthorized."""
        response = self.client.get('/products')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_products_with_invalid_token_returns_401(self):
        """Token giả mạo hoặc sai định dạng phải bị từ chối 401."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"valid": False, "detail": "Token không hợp lệ."}
        self.mock_post.return_value = mock_response

        response = self.client.get(
            '/products',
            HTTP_AUTHORIZATION='Bearer token_sai_hoan_toan_123'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_products_with_expired_token_returns_401(self):
        """Token đã hết hạn phải bị từ chối 401."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"valid": False, "detail": "Token đã hết hạn."}
        self.mock_post.return_value = mock_response

        response = self.client.get(
            '/products',
            HTTP_AUTHORIZATION='Bearer expired_token_xyz'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offline_fallback_jwt_verification(self):
        """Khi Auth Service ngoại tuyến (RequestException), tự động fallback giải mã token nội bộ."""
        import requests
        self.mock_post.side_effect = requests.RequestException("Auth Service unreachable")

        response = self.client.get('/products', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['authenticated_user']['username'], 'test_admin_user')

    # ==========================================
    # 2. KIỂM THỬ CRUD SẢN PHẨM (RESTFUL API TESTS)
    # ==========================================

    def test_get_all_products_success(self):
        """Lấy danh sách sản phẩm với token hợp lệ trả về HTTP 200 OK."""
        response = self.client.get('/products', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.json())
        self.assertEqual(response.json()['total'], 1)
        self.assertEqual(response.json()['data'][0]['name'], self.sample_product.name)

    def test_create_product_success(self):
        """Tạo sản phẩm mới thành công trả về HTTP 201 CREATED."""
        payload = {
            "name": "Bàn phím cơ FL-Esports OG87",
            "description": "Bàn phím không dây 3 chế độ kết nối, layout 87 phím.",
            "price": "2450000.00",
            "quantity": 30
        }
        response = self.client.post('/products', payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['data']['name'], payload['name'])
        self.assertEqual(Decimal(response.json()['data']['price']), Decimal(payload['price']))
        self.assertEqual(response.json()['data']['quantity'], 30)

        # Kiểm tra sản phẩm đã lưu vào database
        self.assertTrue(Product.objects.filter(name=payload['name']).exists())

    def test_create_product_invalid_price_returns_400(self):
        """Tạo sản phẩm với giá âm phải bị từ chối với HTTP 400."""
        payload = {
            "name": "Sản phẩm giá âm",
            "price": "-50000.00",
            "quantity": 10
        }
        response = self.client.post('/products', payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.json())

    def test_create_product_invalid_quantity_returns_400(self):
        """Tạo sản phẩm với số lượng âm phải bị từ chối với HTTP 400."""
        payload = {
            "name": "Sản phẩm số lượng âm",
            "price": "100000.00",
            "quantity": -5
        }
        response = self.client.post('/products', payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_empty_name_returns_400(self):
        """Tạo sản phẩm với tên rỗng phải bị từ chối với HTTP 400."""
        payload = {
            "name": "   ",
            "price": "100000.00",
            "quantity": 5
        }
        response = self.client.post('/products', payload, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_product_detail_success(self):
        """Lấy chi tiết một sản phẩm theo ID trả về HTTP 200 OK."""
        response = self.client.get(f'/products/{self.sample_product.id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()['data']
        self.assertEqual(data['id'], self.sample_product.id)
        self.assertEqual(data['name'], self.sample_product.name)

    def test_get_product_detail_not_found_returns_404(self):
        """Lấy chi tiết sản phẩm với ID không tồn tại trả về HTTP 404."""
        response = self.client.get('/products/999999', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_put_success(self):
        """Cập nhật toàn bộ thông tin sản phẩm (PUT) trả về HTTP 200 OK."""
        payload = {
            "name": "Laptop Gaming ASUS ROG Zephyrus G14 (2024)",
            "description": "Nâng cấp lên 64GB RAM.",
            "price": "45990000.00",
            "quantity": 5
        }
        response = self.client.put(
            f'/products/{self.sample_product.id}',
            payload,
            format='json',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sample_product.refresh_from_db()
        self.assertEqual(self.sample_product.name, payload['name'])
        self.assertEqual(self.sample_product.quantity, 5)

    def test_update_product_patch_success(self):
        """Cập nhật từng phần (PATCH) trả về HTTP 200 OK."""
        payload = {"quantity": 99}
        response = self.client.patch(
            f'/products/{self.sample_product.id}',
            payload,
            format='json',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sample_product.refresh_from_db()
        self.assertEqual(self.sample_product.quantity, 99)

    def test_delete_product_success(self):
        """Xóa sản phẩm theo ID trả về HTTP 200 OK và sản phẩm biến mất khỏi DB."""
        product_id = self.sample_product.id
        response = self.client.delete(f'/products/{product_id}', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(id=product_id).exists())

    def test_delete_product_not_found_returns_404(self):
        """Xóa sản phẩm với ID không tồn tại trả về HTTP 404."""
        response = self.client.delete('/products/999999', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==========================================
    # 3. KIỂM THỬ TÍCH HỢP HTTP VỚI AUTH SERVICE (SOA)
    # ==========================================

    @patch('products.authentication.requests.post')
    def test_auth_service_http_integration_success(self, mock_post):
        """Mô phỏng gọi HTTP thành công sang Auth Service (port 8000)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": True,
            "user": {"IdUser": 10, "UserName": "soa_user"},
            "payload": {"id": 10, "username": "soa_user"}
        }
        mock_post.return_value = mock_response

        response = self.client.get('/products', HTTP_AUTHORIZATION='Bearer remote_token_abc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['authenticated_user']['username'], 'soa_user')

    @patch('products.authentication.requests.post')
    def test_auth_service_http_integration_unauthorized(self, mock_post):
        """Mô phỏng gọi HTTP sang Auth Service bị từ chối 401."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "valid": False,
            "error": "Invalid Token",
            "detail": "Token không hợp lệ hoặc đã bị thu hồi."
        }
        mock_post.return_value = mock_response

        response = self.client.get('/products', HTTP_AUTHORIZATION='Bearer rejected_token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
