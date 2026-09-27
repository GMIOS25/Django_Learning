from django.http import JsonResponse
from .models import User
from .utils import decode_jwt


class JWTAuthenticationMiddleware:
    """
    Middleware xác thực token JWT.
    Thực hiện bảo vệ cho API in dòng 'Hello World' từ bài thực hành số 1
    (đường dẫn /api/hello/ hoặc /hello/).
    
    Các route công khai (public) như Login, Auth, Swagger UI, Admin... sẽ được
    cho phép đi qua mà không bị chặn.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Danh sách các tiền tố/đường dẫn cần bắt buộc xác thực token
        self.protected_routes = [
            '/api/hello',
            '/hello',
        ]

    def __call__(self, request):
        path = request.path.rstrip('/')

        # Kiểm tra xem đường dẫn hiện tại có thuộc nhóm cần bảo vệ không
        is_protected = any(path == route or path.startswith(route + '/') for route in self.protected_routes)

        # Lấy token từ header HTTP Authorization (hoặc query string / header tùy chỉnh)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = None

        if auth_header.startswith('Bearer ') or auth_header.startswith('bearer '):
            token = auth_header[7:].strip()
        elif auth_header:
            token = auth_header.strip()
        elif 'token' in request.GET:
            token = request.GET.get('token')

        request.jwt_user = None
        request.jwt_payload = None

        if token:
            payload, err = decode_jwt(token)
            if payload:
                # Kiểm tra người dùng trong cơ sở dữ liệu
                user_id = payload.get('id')
                user = User.objects.filter(IdUser=user_id).first()
                if user:
                    request.jwt_user = user
                    request.jwt_payload = payload
                else:
                    if is_protected:
                        return JsonResponse({
                            "error": "Unauthorized",
                            "detail": "Người dùng tương ứng với Token không tồn tại trong hệ thống."
                        }, status=401)
            else:
                if is_protected:
                    return JsonResponse({
                        "error": "Unauthorized",
                        "detail": f"Xác thực thất bại: {err}"
                    }, status=401)
        else:
            if is_protected:
                return JsonResponse({
                    "error": "Unauthorized",
                    "detail": "Vui lòng cung cấp JWT token qua Header 'Authorization: Bearer <token>' để truy cập API này."
                }, status=401)

        response = self.get_response(request)
        return response
