from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer chuẩn cho Product theo đầy đủ các trường của đề bài.
    """
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'quantity',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Tên sản phẩm không được để trống.")
        return value.strip()

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Giá sản phẩm phải lớn hơn hoặc bằng 0.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Số lượng sản phẩm không thể là số âm.")
        return value


class ProductResponseSerializer(serializers.Serializer):
    """
    Serializer định dạng response chuẩn trả về cho client.
    """
    message = serializers.CharField()
    data = ProductSerializer(allow_null=True)


class ProductListResponseSerializer(serializers.Serializer):
    """
    Serializer định dạng response cho danh sách sản phẩm.
    """
    total = serializers.IntegerField()
    data = ProductSerializer(many=True)
