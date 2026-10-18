from django.db import models


class Product(models.Model):
    """
    Model đại diện cho bảng sản phẩm (products) theo yêu cầu Phụ lục Bài thực hành số 3.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID duy nhất của sản phẩm'
    )
    name = models.CharField(
        max_length=255,
        db_column='name',
        help_text='Tên sản phẩm'
    )
    description = models.TextField(
        blank=True,
        null=True,
        db_column='description',
        help_text='Mô tả sản phẩm'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='price',
        help_text='Giá sản phẩm'
    )
    quantity = models.IntegerField(
        default=0,
        db_column='quantity',
        help_text='Số lượng sản phẩm trong kho'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        help_text='Ngày sản phẩm được tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        help_text='Ngày sản phẩm được cập nhật lần cuối'
    )

    class Meta:
        db_table = 'products'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Danh sách sản phẩm'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} (ID: {self.id}) - Giá: {self.price} - SL: {self.quantity}"
