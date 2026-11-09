from decimal import Decimal
from rest_framework import serializers
from .models import OrderReport, ProductReport


class ProductReportSerializer(serializers.ModelSerializer):
    """
    Serializer hiển thị thông tin báo cáo sản phẩm (product_reports).
    """
    order_report_id = serializers.IntegerField(source='order_report.id', read_only=True, allow_null=True)

    class Meta:
        model = ProductReport
        fields = [
            'id',
            'order_report_id',
            'product_id',
            'total_sold',
            'revenue',
            'cost',
            'profit',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'profit', 'created_at', 'updated_at']


class OrderReportSerializer(serializers.ModelSerializer):
    """
    Serializer hiển thị báo cáo đơn hàng (orders_reports) kèm danh sách báo cáo sản phẩm con.
    """
    product_reports = ProductReportSerializer(many=True, read_only=True)

    class Meta:
        model = OrderReport
        fields = [
            'id',
            'order_id',
            'total_revenue',
            'total_cost',
            'total_profit',
            'created_at',
            'updated_at',
            'product_reports'
        ]
        read_only_fields = ['id', 'total_profit', 'created_at', 'updated_at', 'product_reports']


class OrderReportCreateSerializer(serializers.Serializer):
    """
    Serializer tiếp nhận yêu cầu tạo báo cáo đơn hàng mới (POST /reports/orders).
    Dịch vụ sẽ tự động liên lạc sang Order Service để lấy doanh thu và các mặt hàng.
    """
    order_id = serializers.IntegerField(
        help_text='ID của đơn hàng từ Order Service'
    )
    total_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Tùy chọn. Tổng chi phí vốn/nhập của đơn hàng. Nếu không truyền, hệ thống sẽ tự động tính theo tỷ lệ vốn mặc định 70% doanh thu.'
    )


class ProductReportCreateSerializer(serializers.Serializer):
    """
    Serializer tiếp nhận yêu cầu tạo báo cáo sản phẩm mới (POST /reports/products).
    """
    product_id = serializers.IntegerField(
        help_text='ID của sản phẩm từ Product Service'
    )
    order_report_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='Tùy chọn. ID của báo cáo đơn hàng liên kết (nếu có).'
    )
    total_sold = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text='Số lượng sản phẩm đã bán. Nếu không truyền, hệ thống sẽ tự động tính từ Order Service.'
    )
    revenue = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Doanh thu từ sản phẩm. Nếu không truyền, hệ thống sẽ tự động tính.'
    )
    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Chi phí vốn nhập hàng. Nếu không truyền, mặc định là 70% doanh thu.'
    )


# Các Serializer tài liệu Swagger/OpenAPI
class OrderReportResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = OrderReportSerializer(allow_null=True)


class OrderReportListResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    total = serializers.IntegerField()
    data = OrderReportSerializer(many=True)


class ProductReportResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = ProductReportSerializer(allow_null=True)


class ProductReportListResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    total = serializers.IntegerField()
    data = ProductReportSerializer(many=True)

