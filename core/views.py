import hashlib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .models import User
from .serializers import LoginSerializer, TokenCheckSerializer, RegisterSerializer, UserResponseSerializer
from .utils import generate_jwt, decode_jwt, verify_password


@extend_schema(
    summary="1. Hello World API (Được bảo vệ bởi Middleware)",
    description="API in dòng 'Hello World' từ bài thực hành số 1. API này được kiểm soát bởi JWTAuthenticationMiddleware; client bắt buộc phải gửi Header `Authorization: Bearer <token>` hợp lệ.",
    responses={
        200: OpenApiResponse(description="Thành công trả về hello-world kèm thông tin user đã xác thực."),
        401: OpenApiResponse(description="Không có token hoặc token không hợp lệ."),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def hello_world(request):
    """
    API in dòng 'hello-world' từ bài thực hành 1.
    Middleware đã thực hiện kiểm tra JWT trước khi request tới được view này.
    """
    user_info = None
    if getattr(request, 'jwt_user', None):
        user_info = {
            'IdUser': request.jwt_user.IdUser,
            'UserName': request.jwt_user.UserName,
        }
    return Response({
        "message": "hello-world",
        "authenticated_user": user_info
    })


@extend_schema(
    summary="2. Dịch vụ Đăng nhập (Sinh JWT Token)",
    description="Nhận userName và password (hỗ trợ Base64 hoặc MD5 từ client). Kiểm tra trong DB và phát hành JWT token, đồng thời lưu vào cột Token của bảng User.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Đăng nhập thành công, trả về JWT token"),
        400: OpenApiResponse(description="Dữ liệu gửi lên không đúng định dạng"),
        401: OpenApiResponse(description="Sai tài khoản hoặc mật khẩu"),
    },
    examples=[
        OpenApiExample(
            "Ví dụ Mật khẩu Base64 ('123456' -> 'MTIzNDU2')",
            value={"userName": "testuser", "password": "MTIzNDU2"}
        ),
        OpenApiExample(
            "Ví dụ Mật khẩu MD5 ('123456' -> 'e10adc3949ba59abbe56e057f20f883e')",
            value={"userName": "testuser", "password": "e10adc3949ba59abbe56e057f20f883e"}
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_name = serializer.validated_data['userName']
    raw_password = serializer.validated_data['password']

    # Tìm người dùng theo UserName trong database
    user = User.objects.filter(UserName=user_name).first()
    if not user:
        return Response({
            "error": "Unauthorized",
            "detail": f"Không tìm thấy tài khoản '{user_name}'."
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Kiểm tra mật khẩu (hỗ trợ Base64 decode, MD5 hash hoặc plain text)
    if not verify_password(raw_password, user.Password):
        return Response({
            "error": "Unauthorized",
            "detail": "Mật khẩu không chính xác."
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Sinh JWT token cho user
    token = generate_jwt(user)

    # Cập nhật cột Token trong bảng User theo yêu cầu phụ lục
    user.Token = token
    user.save(update_fields=['Token'])

    return Response({
        "message": "Đăng nhập thành công",
        "token": token,
        "user": {
            "IdUser": user.IdUser,
            "UserName": user.UserName
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="3. API Xác thực Token (Auth)",
    description="Kiểm tra cấu trúc và tính hợp lệ của token. Có thể truyền token qua Header `Authorization: Bearer <token>` hoặc trong body `{\"token\": \"...\"}`.",
    request=TokenCheckSerializer,
    responses={
        200: OpenApiResponse(description="Token hợp lệ"),
        400: OpenApiResponse(description="Thiếu token"),
        401: OpenApiResponse(description="Token không hợp lệ hoặc đã hết hạn"),
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def auth_view(request):
    token = None

    # 1. Lấy token từ Header Authorization
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer ') or auth_header.startswith('bearer '):
        token = auth_header[7:].strip()
    elif auth_header:
        token = auth_header.strip()

    # 2. Lấy token từ request body nếu là POST
    if not token and request.method == 'POST':
        token = request.data.get('token')

    # 3. Lấy token từ query param ?token=...
    if not token and 'token' in request.GET:
        token = request.GET.get('token')

    if not token:
        return Response({
            "valid": False,
            "error": "Missing Token",
            "detail": "Vui lòng cung cấp token qua Header 'Authorization: Bearer <token>' hoặc body '{\"token\": \"...\"}'."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Giải mã và xác thực token
    payload, err = decode_jwt(token)
    if err:
        return Response({
            "valid": False,
            "error": "Invalid Token",
            "detail": err
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Kiểm tra đối chiếu trong cơ sở dữ liệu
    user = User.objects.filter(IdUser=payload.get('id')).first()
    if not user:
        return Response({
            "valid": False,
            "error": "User Not Found",
            "detail": "Người dùng không tồn tại trong cơ sở dữ liệu."
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "valid": True,
        "message": "Token hợp lệ và còn hiệu lực.",
        "payload": payload,
        "user": {
            "IdUser": user.IdUser,
            "UserName": user.UserName,
            "Token": user.Token
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="4. API Đăng ký tài khoản thử nghiệm",
    description="Tạo người dùng mới trong bảng User để phục vụ kiểm thử.",
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description="Tạo tài khoản thành công"),
        400: OpenApiResponse(description="Tên người dùng đã tồn tại hoặc dữ liệu lỗi"),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_name = serializer.validated_data['userName']
    password = serializer.validated_data['password']

    if User.objects.filter(UserName=user_name).exists():
        return Response({
            "error": f"Tài khoản '{user_name}' đã tồn tại."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Lưu mật khẩu dưới dạng MD5 hash để thống nhất và an toàn
    md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user = User.objects.create(
        UserName=user_name,
        Password=md5_password,
        Token=None
    )

    return Response({
        "message": "Tạo tài khoản thành công!",
        "user": {
            "IdUser": user.IdUser,
            "UserName": user.UserName,
        }
    }, status=status.HTTP_201_CREATED)
