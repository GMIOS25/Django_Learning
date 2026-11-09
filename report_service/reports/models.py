from decimal import Decimal
from django.db import models


class OrderReport(models.Model):
    """
    Model đại diện cho bảng báo cáo đơn hàng (orders_reports) theo Phụ lục Bài thực hành số 5.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID của báo cáo đơn hàng'
    )
    order_id = models.IntegerField(
        db_column='order_id',
        help_text='ID của đơn hàng (lưu vết để liên kết với dịch vụ quản lý đơn hàng)'
    )
    total_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='total_revenue',
        help_text='Tổng doanh thu của đơn hàng'
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='total_cost',
        help_text='Tổng chi phí nhập sản phẩm trong đơn hàng'
    )
    total_profit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='total_profit',
        help_text='Tổng lợi nhuận (total_revenue - total_cost)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        help_text='Thời điểm tạo báo cáo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        help_text='Thời điểm cập nhật báo cáo lần cuối'
    )

    class Meta:
        db_table = 'orders_reports'
        verbose_name = 'Báo cáo đơn hàng'
        verbose_name_plural = 'Danh sách báo cáo đơn hàng'
        ordering = ['-id']

    def __str__(self):
        return f"OrderReport #{self.id} for Order #{self.order_id} - Revenue: {self.total_revenue}, Profit: {self.total_profit}"

    def calculate_profit(self):
        """
        Tính toán lại total_profit = total_revenue - total_cost.
        """
        rev = Decimal(str(self.total_revenue or 0))
        cst = Decimal(str(self.total_cost or 0))
        self.total_profit = rev - cst
        return self.total_profit

    def save(self, *args, **kwargs):
        self.calculate_profit()
        super().save(*args, **kwargs)


class ProductReport(models.Model):
    """
    Model đại diện cho bảng báo cáo sản phẩm (product_reports) theo Phụ lục Bài thực hành số 5.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID của báo cáo sản phẩm'
    )
    order_report = models.ForeignKey(
        OrderReport,
        on_delete=models.CASCADE,
        related_name='product_reports',
        db_column='order_report_id',
        null=True,
        blank=True,
        help_text='ID đơn hàng (liên kết với bảng orders_reports)'
    )
    product_id = models.IntegerField(
        db_column='product_id',
        help_text='ID sản phẩm (lưu vết để liên kết với dịch vụ quản lý sản phẩm)'
    )
    total_sold = models.IntegerField(
        default=0,
        db_column='total_sold',
        help_text='Tổng số lượng sản phẩm đã bán'
    )
    revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='revenue',
        help_text='Doanh thu từ sản phẩm'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='cost',
        help_text='Chi phí nhập sản phẩm'
    )
    profit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='profit',
        help_text='Lợi nhuận (revenue - cost)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        help_text='Thời điểm tạo báo cáo sản phẩm'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        help_text='Thời điểm cập nhật báo cáo lần cuối'
    )

    class Meta:
        db_table = 'product_reports'
        verbose_name = 'Báo cáo sản phẩm'
        verbose_name_plural = 'Danh sách báo cáo sản phẩm'
        ordering = ['-id']

    def __str__(self):
        return f"ProductReport #{self.id} (Product #{self.product_id}) - Sold: {self.total_sold}, Profit: {self.profit}"

    def calculate_profit(self):
        """
        Tính toán lại profit = revenue - cost.
        """
        rev = Decimal(str(self.revenue or 0))
        cst = Decimal(str(self.cost or 0))
        self.profit = rev - cst
        return self.profit

    def save(self, *args, **kwargs):
        self.calculate_profit()
        super().save(*args, **kwargs)

