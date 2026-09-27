import hashlib
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import User
from core.utils import generate_jwt


class JWTAuthAndMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.raw_password = "password123"
        self.md5_password = hashlib.md5(self.raw_password.encode('utf-8')).hexdigest()
        self.base64_password = "cGFzc3dvcmQxMjM="  # base64("password123")

        # Tạo user thử nghiệm
        self.user = User.objects.create(
            UserName="testuser",
            Password=self.md5_password,
            Token=None
        )

    def test_01_login_with_base64_password(self):
        """Kiểm thử đăng nhập bằng mật khẩu mã hóa Base64"""
        response = self.client.post('/login/', {
            'userName': 'testuser',
            'password': self.base64_password
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        token = response.data['token']
        self.assertTrue(len(token) > 20)

        # Kiểm tra token đã được lưu vào database ở cột Token
        self.user.refresh_from_db()
        self.assertEqual(self.user.Token, token)

    def test_02_login_with_md5_password(self):
        """Kiểm thử đăng nhập bằng mật khẩu băm MD5"""
        response = self.client.post('/login/', {
            'userName': 'testuser',
            'password': self.md5_password
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_03_login_with_plain_password(self):
        """Kiểm thử đăng nhập bằng mật khẩu plain text"""
        response = self.client.post('/login/', {
            'userName': 'testuser',
            'password': self.raw_password
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_04_login_wrong_password(self):
        """Kiểm thử đăng nhập sai mật khẩu -> 401 Unauthorized"""
        response = self.client.post('/login/', {
            'userName': 'testuser',
            'password': 'wrongpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_05_auth_token_endpoint(self):
        """Kiểm thử API xác thực token tại /auth"""
        token = generate_jwt(self.user)

        # 1. Gửi qua Header Authorization
        response = self.client.get('/auth', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['user']['UserName'], 'testuser')

        # 2. Gửi qua POST body
        response_post = self.client.post('/auth/', {'token': token}, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_200_OK)
        self.assertTrue(response_post.data['valid'])

    def test_06_middleware_blocks_hello_world_without_token(self):
        """Middleware chặn truy cập /api/hello/ nếu không có token -> 401 Unauthorized"""
        response = self.client.get('/api/hello/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Unauthorized', response.json().get('error', ''))

    def test_07_middleware_blocks_hello_world_with_invalid_token(self):
        """Middleware chặn truy cập /api/hello/ với token sai -> 401 Unauthorized"""
        response = self.client.get('/api/hello/', HTTP_AUTHORIZATION='Bearer invalid.fake.token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_08_middleware_allows_hello_world_with_valid_token(self):
        """Middleware cho phép truy cập /api/hello/ khi có Bearer Token hợp lệ -> 200 OK"""
        token = generate_jwt(self.user)
        response = self.client.get('/api/hello/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'hello-world')
        self.assertEqual(response.data['authenticated_user']['UserName'], 'testuser')

    def test_09_register_endpoint(self):
        """Kiểm thử API đăng ký tài khoản mới"""
        response = self.client.post('/register/', {
            'userName': 'newstudent',
            'password': 'secretpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(UserName='newstudent').exists())
