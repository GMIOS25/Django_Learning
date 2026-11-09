from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer hiển thị đầy đủ thông tin một chi tiết đơn hàng (order_items).
    """
    order_id = serializers.IntegerField(source='order.id', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order_id',
            'product_id',
            'product_name',
            'quantity',
            'unit_price',
            'total_price'
        ]
        read_only_fields = ['id', 'order_id', 'total_price']


class OrderItemNestedInputSerializer(serializers.Serializer):
    """
    Serializer nhập dữ liệu chi tiết sản phẩm lồng trong request tạo đơn hàng (POST /orders).
    """
    product_id = serializers.IntegerField(
        help_text='ID của sản phẩm trong Product Service'
    )
    quantity = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text='Số lượng mua (>= 1)'
    )
    product_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Tùy chọn. Nếu không truyền, hệ thống sẽ tự động lấy từ Product Service.'
    )
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Tùy chọn. Nếu không truyền, hệ thống sẽ tự động lấy từ Product Service.'
    )


class OrderItemCreateSerializer(serializers.Serializer):
    """
    Serializer cho API thêm mới mặt hàng trực tiếp (POST /order_items).
    """
    order_id = serializers.IntegerField(
        help_text='ID của đơn hàng muốn thêm mặt hàng vào'
    )
    product_id = serializers.IntegerField(
        help_text='ID của sản phẩm trong Product Service'
    )
    quantity = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text='Số lượng mua (>= 1)'
    )
    product_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Tùy chọn. Nếu không truyền, hệ thống sẽ tự động lấy từ Product Service.'
    )
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Tùy chọn. Nếu không truyền, hệ thống sẽ tự động lấy từ Product Service.'
    )

    def validate_order_id(self, value):
        if not Order.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Không tìm thấy đơn hàng với ID = {value}.")
        return value


class OrderItemUpdateSerializer(serializers.Serializer):
    """
    Serializer cho API cập nhật mặt hàng (PUT/PATCH /order_items/<id>).
    """
    quantity = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text='Số lượng mới'
    )
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Đơn giá mới'
    )
    product_name = serializers.CharField(
        max_length=255,
        required=False,
        help_text='Tên sản phẩm mới'
    )


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer hiển thị thông tin đơn hàng cùng danh sách chi tiết các mặt hàng.
    """
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'customer_email',
            'total_amount',
            'status',
            'created_at',
            'updated_at',
            'items'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at', 'items']


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer tiếp nhận yêu cầu tạo đơn hàng mới (POST /orders).
    Hỗ trợ tạo đơn hàng kèm luôn danh sách các mặt hàng đặt mua ban đầu.
    """
    customer_name = serializers.CharField(
        max_length=255,
        help_text='Tên khách hàng'
    )
    customer_email = serializers.EmailField(
        help_text='Email khách hàng'
    )
    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES,
        default=Order.STATUS_PENDING,
        required=False,
        help_text='Trạng thái ban đầu của đơn hàng (mặc định: pending)'
    )
    items = OrderItemNestedInputSerializer(
        many=True,
        required=False,
        help_text='Danh sách mặt hàng đặt mua kèm theo'
    )

    def validate_customer_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Tên khách hàng không được để trống.")
        return value.strip()


class OrderUpdateSerializer(serializers.Serializer):
    """
    Serializer cập nhật thông tin đơn hàng / trạng thái đơn hàng (PUT/PATCH /orders/<id>).
    """
    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES,
        required=False,
        help_text='Trạng thái mới của đơn hàng (pending, completed, cancelled)'
    )
    customer_name = serializers.CharField(
        max_length=255,
        required=False,
        help_text='Tên khách hàng mới'
    )
    customer_email = serializers.EmailField(
        required=False,
        help_text='Email khách hàng mới'
    )


# Các Serializer đặc tả phản hồi cho tài liệu Swagger/OpenAPI
class OrderResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = OrderSerializer(allow_null=True)


class OrderListResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    total = serializers.IntegerField()
    data = OrderSerializer(many=True)


class OrderItemResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = OrderItemSerializer(allow_null=True)


class OrderItemListResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    total = serializers.IntegerField()
    data = OrderItemSerializer(many=True)
