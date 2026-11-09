from decimal import Decimal
from django.db import models


class Order(models.Model):
    """
    Model đại diện cho bảng đơn hàng (orders) theo yêu cầu Phụ lục Bài thực hành số 4.
    """
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID duy nhất của đơn hàng'
    )
    customer_name = models.CharField(
        max_length=255,
        db_column='customer_name',
        help_text='Tên khách hàng'
    )
    customer_email = models.CharField(
        max_length=255,
        db_column='customer_email',
        help_text='Email khách hàng'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='total_amount',
        help_text='Tổng số tiền của đơn hàng'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_column='status',
        help_text='Trạng thái của đơn hàng (pending, completed, cancelled)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        help_text='Ngày đơn hàng được tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        help_text='Ngày đơn hàng được cập nhật lần cuối'
    )

    class Meta:
        db_table = 'orders'
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Danh sách đơn hàng'
        ordering = ['-id']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status}) - {self.total_amount} VND"

    def recalculate_total(self):
        """
        Tính lại tổng số tiền total_amount dựa trên tổng total_price của tất cả chi tiết đơn hàng (order_items).
        """
        total = Decimal('0.00')
        for item in self.items.all():
            total += Decimal(str(item.total_price if item.total_price is not None else 0))
        self.total_amount = total
        self.save(update_fields=['total_amount', 'updated_at'])
        return total


class OrderItem(models.Model):
    """
    Model đại diện cho bảng chi tiết đơn hàng (order_items) theo yêu cầu Phụ lục Bài thực hành số 4.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID duy nhất của chi tiết đơn hàng'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='order_id',
        help_text='ID đơn hàng (liên kết với bảng orders)'
    )
    product_id = models.IntegerField(
        db_column='product_id',
        help_text='ID sản phẩm (lưu vết để liên kết với dịch vụ quản lý sản phẩm)'
    )
    product_name = models.CharField(
        max_length=255,
        db_column='product_name',
        help_text='Tên sản phẩm'
    )
    quantity = models.IntegerField(
        default=1,
        db_column='quantity',
        help_text='Số lượng sản phẩm trong đơn hàng'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='unit_price',
        help_text='Giá sản phẩm tại thời điểm đặt hàng'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='total_price',
        help_text='Tổng giá trị cho từng sản phẩm (quantity * unit_price)'
    )

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Danh sách chi tiết đơn hàng'
        ordering = ['id']

    def __str__(self):
        return f"Item #{self.id} in Order #{self.order_id} - {self.product_name} x {self.quantity} = {self.total_price}"

    def save(self, *args, **kwargs):
        """
        Tự động tính total_price = quantity * unit_price trước khi lưu.
        """
        if self.unit_price is not None and self.quantity is not None:
            self.total_price = Decimal(str(self.unit_price)) * Decimal(str(self.quantity))
        super().save(*args, **kwargs)
        if self.order_id:
            self.order.recalculate_total()

    def delete(self, *args, **kwargs):
        """
        Cập nhật lại total_amount của Order cha sau khi xóa item.
        """
        order = self.order
        super().delete(*args, **kwargs)
        if order:
            order.recalculate_total()
