import logging
from decimal import Decimal
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderItemSerializer,
    OrderItemCreateSerializer,
    OrderItemUpdateSerializer,
    OrderResponseSerializer,
    OrderListResponseSerializer,
    OrderItemResponseSerializer,
    OrderItemListResponseSerializer,
)
from .authentication import (
    AuthServiceAuthentication,
    IsAuthServiceAuthenticated,
)
from .product_client import ProductServiceClient

logger = logging.getLogger(__name__)


def _extract_token_from_request(request):
    """
    Trích xuất JWT token để chuyển tiếp sang Product Service / Auth Service.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer ') or auth_header.startswith('bearer '):
        return auth_header[7:].strip()
    if hasattr(request, 'auth') and isinstance(request.auth, str):
        return request.auth
    return None


# ==============================================================================
# 1. ORDER LIST & CREATE: GET /orders, POST /orders
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="1. Lấy danh sách hoặc Tạo mới đơn hàng",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /orders**: Lấy danh sách tất cả các đơn hàng (hỗ trợ lọc `?status=pending|completed|cancelled` và `?search=...`).\n"
        "- **POST /orders**: Tạo đơn hàng mới. Tự động liên lạc sang **Product Service** (cổng 8001) để kiểm tra tồn kho và đơn giá sản phẩm."
    ),
    parameters=[
        OpenApiParameter(
            name='search',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Tìm kiếm theo tên khách hàng hoặc email",
            required=False,
        ),
        OpenApiParameter(
            name='status',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Lọc theo trạng thái đơn hàng (pending, completed, cancelled)",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OrderListResponseSerializer,
            description="Lấy danh sách đơn hàng thành công"
        ),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    }
)
@extend_schema(
    methods=['POST'],
    request=OrderCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=OrderResponseSerializer,
            description="Tạo đơn hàng mới thành công",
            examples=[
                OpenApiExample(
                    "Tạo đơn hàng thành công",
                    value={
                        "message": "Tạo đơn hàng thành công.",
                        "data": {
                            "id": 1,
                            "customer_name": "Nguyễn Văn An",
                            "customer_email": "an.nguyen@example.com",
                            "total_amount": "44790000.00",
                            "status": "pending",
                            "created_at": "2026-10-29T08:20:00Z",
                            "updated_at": "2026-10-29T08:20:00Z",
                            "items": [
                                {
                                    "id": 1,
                                    "order_id": 1,
                                    "product_id": 1,
                                    "product_name": "Laptop Dell XPS 15",
                                    "quantity": 1,
                                    "unit_price": "42500000.00",
                                    "total_price": "42500000.00"
                                }
                            ]
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(description="Dữ liệu không hợp lệ hoặc sản phẩm không đủ tồn kho."),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    },
    examples=[
        OpenApiExample(
            "Ví dụ tạo đơn hàng kèm danh sách sản phẩm",
            value={
                "customer_name": "Nguyễn Văn An",
                "customer_email": "an.nguyen@example.com",
                "status": "pending",
                "items": [
                    {"product_id": 1, "quantity": 1},
                    {"product_id": 3, "quantity": 1}
                ]
            },
            request_only=True
        )
    ]
)
@api_view(['GET', 'POST'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def order_list_create_view(request):
    """
    Controller xử lý:
    - GET /orders: Lấy danh sách tất cả đơn hàng
    - POST /orders: Tạo đơn hàng mới (kiểm tra tồn kho qua Product Service)
    """
    token = _extract_token_from_request(request)

    # -------------------------------------------------------------
    # GET /orders: Lấy danh sách đơn hàng
    # -------------------------------------------------------------
    if request.method == 'GET':
        queryset = Order.objects.all().prefetch_related('items')

        status_param = request.GET.get('status', '').strip().lower()
        if status_param:
            queryset = queryset.filter(status=status_param)

        search_param = request.GET.get('search', '').strip()
        if search_param:
            queryset = queryset.filter(
                models.Q(customer_name__icontains=search_param) |
                models.Q(customer_email__icontains=search_param)
            )

        serializer = OrderSerializer(queryset, many=True)
        return Response({
            'message': 'Lấy danh sách đơn hàng thành công.',
            'total': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # POST /orders: Tạo đơn hàng mới (kiểm tra tồn kho liên dịch vụ)
    # -------------------------------------------------------------
    elif request.method == 'POST':
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Dữ liệu đơn hàng không hợp lệ.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        customer_name = validated_data['customer_name']
        customer_email = validated_data['customer_email']
        order_status = validated_data.get('status', Order.STATUS_PENDING)
        items_data = validated_data.get('items', [])

        # Kiểm tra tồn kho từng sản phẩm với Product Service
        validated_items = []
        for item in items_data:
            pid = item['product_id']
            qty = item.get('quantity', 1)

            is_avail, product_data, err_msg = ProductServiceClient.check_stock(pid, qty, token=token)
            if not is_avail:
                return Response({
                    'message': 'Không thể tạo đơn hàng do vấn đề tồn kho sản phẩm.',
                    'detail': err_msg
                }, status=status.HTTP_400_BAD_REQUEST)

            p_name = item.get('product_name') or (product_data.get('name') if product_data else f"Product #{pid}")
            u_price = item.get('unit_price')
            if u_price is None:
                p_price = product_data.get('price', 0) if product_data else 0
                u_price = Decimal(str(p_price))
            else:
                u_price = Decimal(str(u_price))

            validated_items.append({
                'product_id': pid,
                'product_name': p_name,
                'quantity': qty,
                'unit_price': u_price,
            })

        # Lưu đơn hàng và các mặt hàng trong transaction nguyên tử
        deducted_products = []
        try:
            with transaction.atomic():
                new_order = Order.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    status=order_status,
                )

                for item_dict in validated_items:
                    OrderItem.objects.create(
                        order=new_order,
                        product_id=item_dict['product_id'],
                        product_name=item_dict['product_name'],
                        quantity=item_dict['quantity'],
                        unit_price=item_dict['unit_price'],
                    )

                new_order.recalculate_total()

            # Trừ số lượng tồn kho trên Product Service
            for item_dict in validated_items:
                ok, deduct_err = ProductServiceClient.deduct_stock(
                    item_dict['product_id'],
                    item_dict['quantity'],
                    token=token
                )
                if ok:
                    deducted_products.append((item_dict['product_id'], item_dict['quantity']))
                else:
                    logger.warning(f"Lỗi trừ tồn kho sản phẩm {item_dict['product_id']}: {deduct_err}")

            response_serializer = OrderSerializer(new_order)
            return Response({
                'message': 'Tạo đơn hàng thành công.',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.error(f"Lỗi trong quá trình tạo đơn hàng: {exc}")
            # Hoàn lại tồn kho cho các sản phẩm đã trừ trước khi phát sinh lỗi
            for pid, qty in deducted_products:
                ProductServiceClient.restore_stock(pid, qty, token=token)
            return Response({
                'message': 'Đã xảy ra lỗi khi tạo đơn hàng.',
                'error': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# 2. ORDER DETAIL, UPDATE & DELETE: GET /orders/<id>, PUT /orders/<id>, DELETE /orders/<id>
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="2. Chi tiết, Cập nhật trạng thái và Xóa đơn hàng theo ID",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /orders/<id>**: Lấy thông tin chi tiết một đơn hàng kèm danh sách chi tiết các mặt hàng.\n"
        "- **PUT/PATCH /orders/<id>**: Cập nhật trạng thái đơn hàng (pending, completed, cancelled). "
        "Nếu chuyển sang `cancelled`, hệ thống tự động hoàn trả số lượng tồn kho về **Product Service**.\n"
        "- **DELETE /orders/<id>**: Xóa một đơn hàng (tự động hoàn tồn kho nếu đơn chưa hủy)."
    ),
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của đơn hàng",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(response=OrderResponseSerializer, description="Thành công"),
        404: OpenApiResponse(description="Không tìm thấy đơn hàng với ID cung cấp."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của đơn hàng",
            required=True
        )
    ],
    request=OrderUpdateSerializer,
    responses={
        200: OpenApiResponse(response=OrderResponseSerializer, description="Cập nhật thành công"),
        400: OpenApiResponse(description="Dữ liệu cập nhật không hợp lệ."),
        404: OpenApiResponse(description="Không tìm thấy đơn hàng."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    },
    examples=[
        OpenApiExample(
            "Cập nhật trạng thái đơn hàng sang completed",
            value={"status": "completed"},
            request_only=True
        ),
        OpenApiExample(
            "Hủy đơn hàng (cancelled)",
            value={"status": "cancelled"},
            request_only=True
        )
    ]
)
@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của đơn hàng cần xóa",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description="Xóa đơn hàng thành công"),
        404: OpenApiResponse(description="Không tìm thấy đơn hàng cần xóa."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def order_detail_update_delete_view(request, pk):
    """
    Controller xử lý:
    - GET /orders/<id>: Lấy chi tiết đơn hàng
    - PUT/PATCH /orders/<id>: Cập nhật trạng thái đơn hàng
    - DELETE /orders/<id>: Xóa đơn hàng
    """
    try:
        order = Order.objects.prefetch_related('items').get(pk=pk)
    except Order.DoesNotExist:
        return Response({
            'message': f"Không tìm thấy đơn hàng với ID = {pk}."
        }, status=status.HTTP_404_NOT_FOUND)

    token = _extract_token_from_request(request)

    # -------------------------------------------------------------
    # GET /orders/<id>: Chi tiết đơn hàng
    # -------------------------------------------------------------
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response({
            'message': 'Lấy thông tin chi tiết đơn hàng thành công.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # PUT/PATCH /orders/<id>: Cập nhật trạng thái đơn hàng
    # -------------------------------------------------------------
    elif request.method in ('PUT', 'PATCH'):
        serializer = OrderUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                'message': 'Dữ liệu cập nhật không hợp lệ.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        old_status = order.status
        new_status = validated_data.get('status')

        if 'customer_name' in validated_data and validated_data['customer_name']:
            order.customer_name = validated_data['customer_name']
        if 'customer_email' in validated_data and validated_data['customer_email']:
            order.customer_email = validated_data['customer_email']

        if new_status:
            order.status = new_status
            # Nếu chuyển sang cancelled, tự động hoàn trả tồn kho về Product Service
            if old_status != Order.STATUS_CANCELLED and new_status == Order.STATUS_CANCELLED:
                for item in order.items.all():
                    ProductServiceClient.restore_stock(item.product_id, item.quantity, token=token)

        order.save()
        response_serializer = OrderSerializer(order)
        return Response({
            'message': 'Cập nhật đơn hàng thành công.',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # DELETE /orders/<id>: Xóa một đơn hàng
    # -------------------------------------------------------------
    elif request.method == 'DELETE':
        # Nếu đơn hàng chưa bị cancelled trước đó, hoàn lại tồn kho
        if order.status != Order.STATUS_CANCELLED:
            for item in order.items.all():
                ProductServiceClient.restore_stock(item.product_id, item.quantity, token=token)

        order_id = order.id
        order.delete()
        return Response({
            'message': f"Đã xóa thành công đơn hàng #{order_id}."
        }, status=status.HTTP_200_OK)


# ==============================================================================
# 3. ORDER ITEM LIST & CREATE: GET /order_items, POST /order_items
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="3. Lấy danh sách hoặc Thêm mới mặt hàng trong đơn hàng",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /order_items**: Lấy danh sách tất cả các mặt hàng (hỗ trợ lọc `?order_id=<id>`).\n"
        "- **POST /order_items**: Tạo mặt hàng mới trong đơn hàng, tự động kiểm tra tồn kho từ Product Service và cập nhật lại `total_amount` của đơn hàng."
    ),
    parameters=[
        OpenApiParameter(
            name='order_id',
            type=int,
            location=OpenApiParameter.QUERY,
            description="Lọc danh sách mặt hàng thuộc về một đơn hàng cụ thể",
            required=False
        )
    ],
    responses={
        200: OpenApiResponse(response=OrderItemListResponseSerializer, description="Lấy danh sách mặt hàng thành công"),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    }
)
@extend_schema(
    methods=['POST'],
    request=OrderItemCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=OrderItemResponseSerializer,
            description="Tạo mặt hàng mới thành công",
            examples=[
                OpenApiExample(
                    "Ví dụ thêm một mặt hàng vào đơn hàng",
                    value={
                        "order_id": 1,
                        "product_id": 3,
                        "quantity": 2
                    }
                )
            ]
        ),
        400: OpenApiResponse(description="Dữ liệu mặt hàng không hợp lệ hoặc sản phẩm không đủ tồn kho."),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    }
)
@api_view(['GET', 'POST'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def order_item_list_create_view(request):
    """
    Controller xử lý:
    - GET /order_items: Lấy danh sách tất cả mặt hàng trong đơn hàng
    - POST /order_items: Tạo mặt hàng mới (kiểm tra tồn kho qua Product Service)
    """
    token = _extract_token_from_request(request)

    # -------------------------------------------------------------
    # GET /order_items: Lấy danh sách mặt hàng
    # -------------------------------------------------------------
    if request.method == 'GET':
        queryset = OrderItem.objects.select_related('order').all()
        order_id = request.GET.get('order_id')
        if order_id:
            try:
                queryset = queryset.filter(order_id=int(order_id))
            except ValueError:
                return Response({
                    'message': 'order_id phải là số nguyên.'
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderItemSerializer(queryset, many=True)
        return Response({
            'message': 'Lấy danh sách mặt hàng thành công.',
            'total': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # POST /order_items: Tạo mặt hàng mới
    # -------------------------------------------------------------
    elif request.method == 'POST':
        serializer = OrderItemCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Dữ liệu mặt hàng không hợp lệ.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        order_id = validated_data['order_id']
        product_id = validated_data['product_id']
        quantity = validated_data.get('quantity', 1)

        try:
            target_order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({
                'message': f"Không tìm thấy đơn hàng với ID = {order_id}."
            }, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra tồn kho từ Product Service
        is_avail, product_data, err_msg = ProductServiceClient.check_stock(product_id, quantity, token=token)
        if not is_avail:
            return Response({
                'message': 'Không thể thêm mặt hàng do tồn kho không đủ.',
                'detail': err_msg
            }, status=status.HTTP_400_BAD_REQUEST)

        product_name = validated_data.get('product_name') or (product_data.get('name') if product_data else f"Product #{product_id}")
        unit_price = validated_data.get('unit_price')
        if unit_price is None:
            p_price = product_data.get('price', 0) if product_data else 0
            unit_price = Decimal(str(p_price))
        else:
            unit_price = Decimal(str(unit_price))

        try:
            with transaction.atomic():
                order_item = OrderItem.objects.create(
                    order=target_order,
                    product_id=product_id,
                    product_name=product_name,
                    quantity=quantity,
                    unit_price=unit_price,
                )
                target_order.recalculate_total()

            # Trừ tồn kho trên Product Service
            ProductServiceClient.deduct_stock(product_id, quantity, token=token)

            response_serializer = OrderItemSerializer(order_item)
            return Response({
                'message': 'Thêm mặt hàng vào đơn hàng thành công.',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.error(f"Lỗi khi thêm mặt hàng vào đơn: {exc}")
            return Response({
                'message': 'Đã xảy ra lỗi khi thêm mặt hàng vào đơn.',
                'error': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# 4. ORDER ITEM DETAIL, UPDATE & DELETE: GET/PUT/PATCH/DELETE /order_items/<id>
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="4. Chi tiết, Cập nhật và Xóa một mặt hàng theo ID",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /order_items/<id>**: Lấy thông tin chi tiết một mặt hàng.\n"
        "- **PUT/PATCH /order_items/<id>**: Cập nhật mặt hàng (tự động tính lại tổng tiền đơn hàng).\n"
        "- **DELETE /order_items/<id>**: Xóa một mặt hàng khỏi đơn hàng (tự động tính lại tổng tiền đơn hàng)."
    ),
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của chi tiết đơn hàng",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(response=OrderItemResponseSerializer, description="Lấy chi tiết mặt hàng thành công"),
        404: OpenApiResponse(description="Không tìm thấy mặt hàng với ID cung cấp."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của chi tiết đơn hàng",
            required=True
        )
    ],
    request=OrderItemUpdateSerializer,
    responses={
        200: OpenApiResponse(response=OrderItemResponseSerializer, description="Cập nhật mặt hàng thành công"),
        400: OpenApiResponse(description="Dữ liệu cập nhật không hợp lệ."),
        404: OpenApiResponse(description="Không tìm thấy mặt hàng cần cập nhật."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của chi tiết đơn hàng cần xóa",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description="Xóa mặt hàng khỏi đơn hàng thành công"),
        404: OpenApiResponse(description="Không tìm thấy mặt hàng cần xóa."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def order_item_detail_update_delete_view(request, pk):
    """
    Controller xử lý:
    - GET /order_items/<id>: Lấy thông tin chi tiết một mặt hàng
    - PUT/PATCH /order_items/<id>: Cập nhật mặt hàng
    - DELETE /order_items/<id>: Xóa một mặt hàng trong đơn hàng
    """
    try:
        item = OrderItem.objects.select_related('order').get(pk=pk)
    except OrderItem.DoesNotExist:
        return Response({
            'message': f"Không tìm thấy chi tiết mặt hàng với ID = {pk}."
        }, status=status.HTTP_404_NOT_FOUND)

    token = _extract_token_from_request(request)

    # -------------------------------------------------------------
    # GET /order_items/<id>: Chi tiết mặt hàng
    # -------------------------------------------------------------
    if request.method == 'GET':
        serializer = OrderItemSerializer(item)
        return Response({
            'message': 'Lấy thông tin chi tiết mặt hàng thành công.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # PUT/PATCH /order_items/<id>: Cập nhật mặt hàng
    # -------------------------------------------------------------
    elif request.method in ('PUT', 'PATCH'):
        serializer = OrderItemUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                'message': 'Dữ liệu cập nhật không hợp lệ.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        old_quantity = item.quantity
        new_quantity = validated_data.get('quantity')

        if new_quantity is not None and new_quantity != old_quantity:
            qty_diff = new_quantity - old_quantity
            if qty_diff > 0:
                # Cần thêm số lượng -> kiểm tra tồn kho
                is_avail, _, err = ProductServiceClient.check_stock(item.product_id, qty_diff, token=token)
                if not is_avail:
                    return Response({
                        'message': 'Không thể cập nhật số lượng do tồn kho không đủ.',
                        'detail': err
                    }, status=status.HTTP_400_BAD_REQUEST)
                ProductServiceClient.deduct_stock(item.product_id, qty_diff, token=token)
            else:
                # Giảm số lượng -> hoàn lại tồn kho
                ProductServiceClient.restore_stock(item.product_id, abs(qty_diff), token=token)
            item.quantity = new_quantity

        if 'unit_price' in validated_data and validated_data['unit_price'] is not None:
            item.unit_price = Decimal(str(validated_data['unit_price']))
        if 'product_name' in validated_data and validated_data['product_name']:
            item.product_name = validated_data['product_name']

        item.save()
        if item.order:
            item.order.recalculate_total()

        response_serializer = OrderItemSerializer(item)
        return Response({
            'message': 'Cập nhật mặt hàng thành công.',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # DELETE /order_items/<id>: Xóa một mặt hàng khỏi đơn hàng
    # -------------------------------------------------------------
    elif request.method == 'DELETE':
        order = item.order
        if order and order.status != Order.STATUS_CANCELLED:
            ProductServiceClient.restore_stock(item.product_id, item.quantity, token=token)

        item_id = item.id
        item.delete()
        if order:
            order.recalculate_total()

        return Response({
            'message': f"Đã xóa thành công mặt hàng #{item_id} khỏi đơn hàng."
        }, status=status.HTTP_200_OK)

