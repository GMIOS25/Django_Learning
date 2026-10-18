from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from .models import Product
from .serializers import ProductSerializer, ProductListResponseSerializer, ProductResponseSerializer
from .authentication import AuthServiceAuthentication, IsAuthServiceAuthenticated


@extend_schema(
    summary="1. Lấy danh sách hoặc Thêm mới sản phẩm",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Gửi kèm header `Authorization: Bearer <token>`.\n\n"
        "- **GET /products**: Lấy danh sách tất cả các sản phẩm trong cơ sở dữ liệu riêng của Product Service.\n"
        "- **POST /products**: Tạo mới một sản phẩm (yêu cầu `name`, `price`, `quantity`, `description`)."
    ),
    methods=['GET'],
    responses={
        200: OpenApiResponse(description="Danh sách sản phẩm thành công", response=ProductListResponseSerializer),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    }
)
@extend_schema(
    methods=['POST'],
    request=ProductSerializer,
    responses={
        201: OpenApiResponse(description="Tạo sản phẩm thành công", response=ProductResponseSerializer),
        400: OpenApiResponse(description="Dữ liệu sản phẩm không hợp lệ."),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    },
    examples=[
        OpenApiExample(
            "Ví dụ thêm sản phẩm mới",
            value={
                "name": "Bàn phím cơ không dây Keychron K2",
                "description": "Bàn phím cơ Bluetooth layout 75%, hot-swap switch Gateron G Pro.",
                "price": "1850000.00",
                "quantity": 25
            }
        )
    ]
)
@api_view(['GET', 'POST'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def product_list_create_view(request):
    """
    Controller xử lý nghiệp vụ cho:
    - GET /products: Lấy toàn bộ danh sách sản phẩm
    - POST /products: Tạo sản phẩm mới
    """
    if request.method == 'GET':
        # Hỗ trợ tìm kiếm nhanh theo tên sản phẩm nếu có query param ?search=
        search_query = request.GET.get('search', '').strip()
        queryset = Product.objects.all()
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        serializer = ProductSerializer(queryset, many=True)
        return Response({
            "message": "Lấy danh sách sản phẩm thành công.",
            "total": queryset.count(),
            "authenticated_user": {
                "id": request.user.id,
                "username": request.user.username
            },
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "message": "Dữ liệu thêm sản phẩm không hợp lệ.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        product = serializer.save()
        return Response({
            "message": "Thêm mới sản phẩm thành công.",
            "authenticated_user": {
                "id": request.user.id,
                "username": request.user.username
            },
            "data": ProductSerializer(product).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="2. Chi tiết, Cập nhật và Xóa sản phẩm theo ID",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Gửi kèm header `Authorization: Bearer <token>`.\n\n"
        "- **GET /products/<id>**: Lấy thông tin chi tiết một sản phẩm theo ID.\n"
        "- **PUT /products/<id>**: Cập nhật toàn bộ thông tin sản phẩm.\n"
        "- **PATCH /products/<id>**: Cập nhật từng phần thông tin sản phẩm.\n"
        "- **DELETE /products/<id>**: Xóa một sản phẩm theo ID."
    ),
    parameters=[
        OpenApiParameter(name='pk', description='ID duy nhất của sản phẩm', required=True, type=int, location=OpenApiParameter.PATH)
    ],
    methods=['GET'],
    responses={
        200: OpenApiResponse(description="Lấy chi tiết sản phẩm thành công", response=ProductResponseSerializer),
        404: OpenApiResponse(description="Không tìm thấy sản phẩm với ID cung cấp."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    request=ProductSerializer,
    responses={
        200: OpenApiResponse(description="Cập nhật sản phẩm thành công", response=ProductResponseSerializer),
        400: OpenApiResponse(description="Dữ liệu cập nhật không hợp lệ."),
        404: OpenApiResponse(description="Không tìm thấy sản phẩm cần cập nhật."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    },
    examples=[
        OpenApiExample(
            "Ví dụ cập nhật giá và số lượng",
            value={
                "name": "Bàn phím cơ không dây Keychron K2 V2",
                "description": "Bản nâng cấp switch Gateron Pro, pin 4000mAh.",
                "price": "1950000.00",
                "quantity": 18
            }
        )
    ]
)
@extend_schema(
    methods=['DELETE'],
    responses={
        200: OpenApiResponse(description="Xóa sản phẩm thành công"),
        404: OpenApiResponse(description="Không tìm thấy sản phẩm cần xóa."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def product_detail_update_delete_view(request, pk):
    """
    Controller xử lý nghiệp vụ cho:
    - GET /products/<id>: Lấy thông tin chi tiết sản phẩm
    - PUT /products/<id>: Cập nhật thông tin sản phẩm
    - PATCH /products/<id>: Cập nhật từng phần thông tin sản phẩm
    - DELETE /products/<id>: Xóa sản phẩm
    """
    product = Product.objects.filter(pk=pk).first()
    if not product:
        return Response({
            "error": "Not Found",
            "detail": f"Không tìm thấy sản phẩm có ID = {pk}."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response({
            "message": "Lấy thông tin chi tiết sản phẩm thành công.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = ProductSerializer(product, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response({
                "message": "Dữ liệu cập nhật sản phẩm không hợp lệ.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        updated_product = serializer.save()
        return Response({
            "message": f"Cập nhật thông tin sản phẩm ID = {pk} thành công.",
            "data": ProductSerializer(updated_product).data
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        deleted_id = product.id
        deleted_name = product.name
        product.delete()
        return Response({
            "message": f"Đã xóa thành công sản phẩm '{deleted_name}' (ID = {deleted_id}).",
            "deleted_id": deleted_id
        }, status=status.HTTP_200_OK)
