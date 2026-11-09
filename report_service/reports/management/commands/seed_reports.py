from decimal import Decimal
from django.core.management.base import BaseCommand
from reports.models import OrderReport, ProductReport


class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho Reporting Service (Bài Thực Hành Số 5)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Đang khởi tạo dữ liệu mẫu cho Reporting Service..."))

        if OrderReport.objects.exists():
            self.stdout.write(self.style.WARNING("Dữ liệu báo cáo đã tồn tại. Bỏ qua khởi tạo."))
            return

        # Báo cáo cho đơn hàng 1 (Doanh thu 44,790,000 VND)
        rep1 = OrderReport.objects.create(
            order_id=1,
            total_revenue=Decimal("44790000.00"),
            total_cost=Decimal("31353000.00"),
        )
        ProductReport.objects.create(
            order_report=rep1,
            product_id=1,
            total_sold=1,
            revenue=Decimal("42500000.00"),
            cost=Decimal("29750000.00"),
        )
        ProductReport.objects.create(
            order_report=rep1,
            product_id=3,
            total_sold=1,
            revenue=Decimal("2290000.00"),
            cost=Decimal("1603000.00"),
        )

        # Báo cáo cho đơn hàng 2 (Doanh thu 16,690,000 VND)
        rep2 = OrderReport.objects.create(
            order_id=2,
            total_revenue=Decimal("16690000.00"),
            total_cost=Decimal("11683000.00"),
        )
        ProductReport.objects.create(
            order_report=rep2,
            product_id=2,
            total_sold=2,
            revenue=Decimal("9700000.00"),
            cost=Decimal("6790000.00"),
        )
        ProductReport.objects.create(
            order_report=rep2,
            product_id=4,
            total_sold=1,
            revenue=Decimal("6990000.00"),
            cost=Decimal("4893000.00"),
        )

        # Báo cáo độc lập cho sản phẩm 5 (Màn hình Dell UltraSharp 4K)
        ProductReport.objects.create(
            order_report=None,
            product_id=5,
            total_sold=3,
            revenue=Decimal("38700000.00"),
            cost=Decimal("27090000.00"),
        )

        self.stdout.write(self.style.SUCCESS("Khởi tạo thành công dữ liệu báo cáo mẫu!"))

