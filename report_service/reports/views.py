import logging
from decimal import Decimal
from django.db import transaction, models
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from .models import OrderReport, ProductReport
from .serializers import (
    OrderReportSerializer,
    OrderReportCreateSerializer,
    ProductReportSerializer,
    ProductReportCreateSerializer,
    OrderReportResponseSerializer,
    OrderReportListResponseSerializer,
    ProductReportResponseSerializer,
    ProductReportListResponseSerializer,
)
from .authentication import (
    AuthServiceAuthentication,
    IsAuthServiceAuthenticated,
)
from .service_clients import OrderServiceClient, ProductServiceClient

logger = logging.getLogger(__name__)


def _extract_token_from_request(request):
    """
    Trích xuất JWT token để chuyển tiếp sang Auth / Order / Product Service.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer ') or auth_header.startswith('bearer '):
        return auth_header[7:].strip()
    if hasattr(request, 'auth') and isinstance(request.auth, str):
        return request.auth
    return None


# ==============================================================================
# 1. ORDER REPORTS: GET /reports/orders, POST /reports/orders
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="1. Lấy danh sách hoặc Tạo mới báo cáo theo đơn hàng",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /reports/orders**: Lấy danh sách tất cả các báo cáo theo đơn hàng (hỗ trợ lọc `?order_id=<id>`).\n"
        "- **POST /reports/orders**: Tạo báo cáo đơn hàng mới dựa trên dữ liệu từ dịch vụ quản lý đơn hàng (cổng 8002)."
    ),
    parameters=[
        OpenApiParameter(
            name='order_id',
            type=int,
            location=OpenApiParameter.QUERY,
            description="Lọc báo cáo theo ID đơn hàng cụ thể",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(response=OrderReportListResponseSerializer, description="Thành công"),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    }
)
@extend_schema(
    methods=['POST'],
    request=OrderReportCreateSerializer,
    responses={
        201: OpenApiResponse(response=OrderReportResponseSerializer, description="Tạo báo cáo đơn hàng thành công"),
        400: OpenApiResponse(description="Dữ liệu không hợp lệ hoặc lỗi liên dịch vụ."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
        404: OpenApiResponse(description="Không tìm thấy đơn hàng trên Order Service."),
    },
    examples=[
        OpenApiExample(
            "Ví dụ tạo báo cáo đơn hàng",
            value={"order_id": 1, "total_cost": "31353000.00"},
            request_only=True
        )
    ]
)
@api_view(['GET', 'POST'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def order_reports_list_create_view(request):
    """
    Controller xử lý:
    - GET /reports/orders: Lấy danh sách tất cả các báo cáo theo đơn hàng
    - POST /reports/orders: Tạo báo cáo đơn hàng mới dựa trên dữ liệu từ dịch vụ quản lý đơn hàng
    """
    token = _extract_token_from_request(request)

    # -------------------------------------------------------------
    # GET /reports/orders
    # -------------------------------------------------------------
    if request.method == 'GET':
        queryset = OrderReport.objects.prefetch_related('product_reports').all()
        order_id = request.GET.get('order_id')
        if order_id:
            try:
                queryset = queryset.filter(order_id=int(order_id))
            except ValueError:
                return Response({
                    'message': 'order_id phải là số nguyên.'
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderReportSerializer(queryset, many=True)
        return Response({
            'message': 'Lấy danh sách báo cáo đơn hàng thành công.',
            'total': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # POST /reports/orders: Tạo báo cáo đơn hàng từ dữ liệu Order Service
    # -------------------------------------------------------------
    elif request.method == 'POST':
        serializer = OrderReportCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Dữ liệu yêu cầu không hợp lệ.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        custom_cost = serializer.validated_data.get('total_cost')

        # Gọi sang Order Service (cổng 8002) để lấy dữ liệu đơn hàng
        order_data, err = OrderServiceClient.get_order(order_id, token=token)
        if err or not order_data:
            return Response({
                'message': 'Không thể lấy dữ liệu đơn hàng từ Order Service.',
                'detail': err or f"Không tìm thấy đơn hàng ID {order_id}."
            }, status=status.HTTP_404_NOT_FOUND if "Không tìm thấy" in str(err) else status.HTTP_400_BAD_REQUEST)

        total_revenue = Decimal(str(order_data.get('total_amount', 0)))

        # Nếu người dùng không nhập total_cost, áp dụng quy tắc tỷ lệ giá vốn 70% doanh thu
        if custom_cost is not None:
            total_cost = Decimal(str(custom_cost))
        else:
            total_cost = (total_revenue * Decimal('0.70')).quantize(Decimal('0.01'))

        try:
            with transaction.atomic():
                order_report = OrderReport.objects.create(
                    order_id=order_id,
                    total_revenue=total_revenue,
                    total_cost=total_cost,
                )

                # Tự động tạo các product_reports tương ứng từ items của đơn hàng
                items = order_data.get('items', [])
                for item in items:
                    pid = item.get('product_id')
                    qty = item.get('quantity', 1)
                    item_rev = Decimal(str(item.get('total_price', 0)))
                    item_cost = (item_rev * Decimal('0.70')).quantize(Decimal('0.01'))

                    ProductReport.objects.create(
                        order_report=order_report,
                        product_id=pid,
                        total_sold=qty,
                        revenue=item_rev,
                        cost=item_cost,
                    )

            response_serializer = OrderReportSerializer(order_report)
            return Response({
                'message': 'Tạo báo cáo đơn hàng thành công.',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.error(f"Lỗi khi tạo báo cáo đơn hàng: {exc}")
            return Response({
                'message': 'Đã xảy ra lỗi khi tạo báo cáo đơn hàng.',
                'error': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# 2. ORDER REPORT DETAIL & DELETE: GET /reports/orders/<id>, DELETE /reports/orders/<id>
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="2. Chi tiết báo cáo đơn hàng theo ID",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /reports/orders/<id>**: Lấy chi tiết báo cáo cho một đơn hàng kèm các mặt hàng con."
    ),
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của báo cáo đơn hàng",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(response=OrderReportResponseSerializer, description="Thành công"),
        404: OpenApiResponse(description="Không tìm thấy báo cáo đơn hàng."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@extend_schema(
    methods=['DELETE'],
    summary="3. Xóa báo cáo đơn hàng",
    description="- **DELETE /reports/orders/<id>**: Xóa báo cáo đơn hàng (tự động xóa các báo cáo sản phẩm con).",
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của báo cáo đơn hàng cần xóa",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description="Xóa báo cáo đơn hàng thành công"),
        404: OpenApiResponse(description="Không tìm thấy báo cáo đơn hàng cần xóa."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@api_view(['GET', 'DELETE'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def order_reports_detail_delete_view(request, pk):
    """
    Controller xử lý:
    - GET /reports/orders/<id>: Lấy chi tiết báo cáo cho một đơn hàng
    - DELETE /reports/orders/<id>: Xóa báo cáo đơn hàng
    """
    try:
        report = OrderReport.objects.prefetch_related('product_reports').get(pk=pk)
    except OrderReport.DoesNotExist:
        return Response({
            'message': f"Không tìm thấy báo cáo đơn hàng với ID = {pk}."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrderReportSerializer(report)
        return Response({
            'message': 'Lấy thông tin chi tiết báo cáo đơn hàng thành công.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        rep_id = report.id
        report.delete()
        return Response({
            'message': f"Đã xóa thành công báo cáo đơn hàng #{rep_id}."
        }, status=status.HTTP_200_OK)


# ==============================================================================
# 3. PRODUCT REPORTS: GET /reports/products, POST /reports/products
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="4. Lấy danh sách hoặc Tạo mới báo cáo theo sản phẩm",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /reports/products**: Lấy danh sách tất cả các báo cáo theo sản phẩm (hỗ trợ lọc `?product_id=<id>`).\n"
        "- **POST /reports/products**: Tạo báo cáo sản phẩm mới dựa trên dữ liệu từ dịch vụ quản lý sản phẩm và quản lý đơn hàng."
    ),
    parameters=[
        OpenApiParameter(
            name='product_id',
            type=int,
            location=OpenApiParameter.QUERY,
            description="Lọc báo cáo theo ID sản phẩm",
            required=False
        )
    ],
    responses={
        200: OpenApiResponse(response=ProductReportListResponseSerializer, description="Thành công"),
        401: OpenApiResponse(description="Chưa đăng nhập hoặc token không hợp lệ."),
    }
)
@extend_schema(
    methods=['POST'],
    request=ProductReportCreateSerializer,
    responses={
        201: OpenApiResponse(response=ProductReportResponseSerializer, description="Tạo báo cáo sản phẩm thành công"),
        400: OpenApiResponse(description="Dữ liệu không hợp lệ."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    },
    examples=[
        OpenApiExample(
            "Ví dụ tạo báo cáo sản phẩm",
            value={
                "product_id": 1,
                "total_sold": 5,
                "revenue": "212500000.00",
                "cost": "148750000.00"
            },
            request_only=True
        )
    ]
)
@api_view(['GET', 'POST'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def product_reports_list_create_view(request):
    """
    Controller xử lý:
    - GET /reports/products: Lấy danh sách tất cả các báo cáo theo sản phẩm
    - POST /reports/products: Tạo báo cáo sản phẩm mới dựa trên dữ liệu từ dịch vụ quản lý sản phẩm và đơn hàng
    """
    token = _extract_token_from_request(request)

    # -------------------------------------------------------------
    # GET /reports/products
    # -------------------------------------------------------------
    if request.method == 'GET':
        queryset = ProductReport.objects.select_related('order_report').all()
        product_id = request.GET.get('product_id')
        if product_id:
            try:
                queryset = queryset.filter(product_id=int(product_id))
            except ValueError:
                return Response({
                    'message': 'product_id phải là số nguyên.'
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductReportSerializer(queryset, many=True)
        return Response({
            'message': 'Lấy danh sách báo cáo sản phẩm thành công.',
            'total': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------------------------------------
    # POST /reports/products: Tạo báo cáo sản phẩm mới
    # -------------------------------------------------------------
    elif request.method == 'POST':
        serializer = ProductReportCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Dữ liệu không hợp lệ.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        product_id = validated_data['product_id']
        order_report_id = validated_data.get('order_report_id')
        total_sold = validated_data.get('total_sold')
        revenue = validated_data.get('revenue')
        cost = validated_data.get('cost')

        order_report = None
        if order_report_id:
            try:
                order_report = OrderReport.objects.get(pk=order_report_id)
            except OrderReport.DoesNotExist:
                return Response({
                    'message': f"Không tìm thấy báo cáo đơn hàng với ID = {order_report_id}."
                }, status=status.HTTP_404_NOT_FOUND)

        # Nếu revenue hoặc total_sold không truyền, thử lấy thông tin giá từ Product Service
        if revenue is None:
            prod_data, prod_err = ProductServiceClient.get_product(product_id, token=token)
            unit_price = Decimal(str(prod_data.get('price', 0))) if prod_data else Decimal('0.00')
            sold_count = total_sold if total_sold is not None else 1
            revenue = unit_price * Decimal(str(sold_count))
            if total_sold is None:
                total_sold = sold_count
        else:
            revenue = Decimal(str(revenue))
            if total_sold is None:
                total_sold = 1

        # Nếu cost không truyền, mặc định chi phí là 70% revenue
        if cost is None:
            cost = (revenue * Decimal('0.70')).quantize(Decimal('0.01'))
        else:
            cost = Decimal(str(cost))

        try:
            product_report = ProductReport.objects.create(
                order_report=order_report,
                product_id=product_id,
                total_sold=total_sold,
                revenue=revenue,
                cost=cost,
            )
            response_serializer = ProductReportSerializer(product_report)
            return Response({
                'message': 'Tạo báo cáo sản phẩm thành công.',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.error(f"Lỗi khi tạo báo cáo sản phẩm: {exc}")
            return Response({
                'message': 'Đã xảy ra lỗi khi tạo báo cáo sản phẩm.',
                'error': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# 4. PRODUCT REPORT DETAIL & DELETE: GET /reports/products/<id>, DELETE /reports/products/<id>
# ==============================================================================
@extend_schema(
    methods=['GET'],
    summary="5. Chi tiết báo cáo sản phẩm theo ID",
    description=(
        "**Yêu cầu xác thực qua Auth Service (Bài 2)**: Header `Authorization: Bearer <token>`.\n\n"
        "- **GET /reports/products/<id>**: Lấy chi tiết báo cáo cho một sản phẩm."
    ),
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của báo cáo sản phẩm",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(response=ProductReportResponseSerializer, description="Thành công"),
        404: OpenApiResponse(description="Không tìm thấy báo cáo sản phẩm."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@extend_schema(
    methods=['DELETE'],
    summary="6. Xóa báo cáo sản phẩm",
    description="- **DELETE /reports/products/<id>**: Xóa báo cáo sản phẩm.",
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description="ID của báo cáo sản phẩm cần xóa",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description="Xóa báo cáo sản phẩm thành công"),
        404: OpenApiResponse(description="Không tìm thấy báo cáo sản phẩm cần xóa."),
        401: OpenApiResponse(description="Chưa xác thực qua Auth Service."),
    }
)
@api_view(['GET', 'DELETE'])
@authentication_classes([AuthServiceAuthentication])
@permission_classes([IsAuthServiceAuthenticated])
def product_reports_detail_delete_view(request, pk):
    """
    Controller xử lý:
    - GET /reports/products/<id>: Lấy chi tiết báo cáo cho một sản phẩm
    - DELETE /reports/products/<id>: Xóa báo cáo sản phẩm
    """
    try:
        report = ProductReport.objects.select_related('order_report').get(pk=pk)
    except ProductReport.DoesNotExist:
        return Response({
            'message': f"Không tìm thấy báo cáo sản phẩm với ID = {pk}."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductReportSerializer(report)
        return Response({
            'message': 'Lấy thông tin chi tiết báo cáo sản phẩm thành công.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        rep_id = report.id
        report.delete()
        return Response({
            'message': f"Đã xóa thành công báo cáo sản phẩm #{rep_id}."
        }, status=status.HTTP_200_OK)

