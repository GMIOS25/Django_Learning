from decimal import Decimal
from django.core.management.base import BaseCommand
from orders.models import Order, OrderItem


class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho Order Service (Bài Thực Hành Số 4)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Đang khởi tạo dữ liệu mẫu cho Order Service..."))

        if Order.objects.exists():
            self.stdout.write(self.style.WARNING("Dữ liệu đơn hàng đã tồn tại. Bỏ qua khởi tạo."))
            return

        # Đơn hàng 1
        order1 = Order.objects.create(
            customer_name="Nguyen Van An",
            customer_email="an.nguyen@example.com",
            status=Order.STATUS_COMPLETED,
        )
        OrderItem.objects.create(
            order=order1,
            product_id=1,
            product_name="Laptop Dell XPS 15 9530",
            quantity=1,
            unit_price=Decimal("42500000.00"),
        )
        OrderItem.objects.create(
            order=order1,
            product_id=3,
            product_name="Chuot cong thai hoc Logitech MX Master 3S",
            quantity=1,
            unit_price=Decimal("2290000.00"),
        )

        # Đơn hàng 2
        order2 = Order.objects.create(
            customer_name="Tran Thi Bich",
            customer_email="bich.tran@example.com",
            status=Order.STATUS_PENDING,
        )
        OrderItem.objects.create(
            order=order2,
            product_id=2,
            product_name="Ban phim co khong day Keychron Q1 Pro",
            quantity=2,
            unit_price=Decimal("4850000.00"),
        )
        OrderItem.objects.create(
            order=order2,
            product_id=4,
            product_name="Tai nghe chong on Sony WH-1000XM5",
            quantity=1,
            unit_price=Decimal("6990000.00"),
        )

        # Đơn hàng 3
        order3 = Order.objects.create(
            customer_name="Le Hoang Nam",
            customer_email="nam.le@example.com",
            status=Order.STATUS_CANCELLED,
        )
        OrderItem.objects.create(
            order=order3,
            product_id=5,
            product_name="Man hinh Dell UltraSharp U2723QE 27 inch 4K",
            quantity=1,
            unit_price=Decimal("12900000.00"),
        )

        # Đơn hàng 4
        order4 = Order.objects.create(
            customer_name="Pham Minh Duc",
            customer_email="duc.pham@example.com",
            status=Order.STATUS_PENDING,
        )
        OrderItem.objects.create(
            order=order4,
            product_id=3,
            product_name="Chuot cong thai hoc Logitech MX Master 3S",
            quantity=2,
            unit_price=Decimal("2290000.00"),
        )

        self.stdout.write(self.style.SUCCESS(f"Khởi tạo thành công 4 đơn hàng và 6 mặt hàng mẫu!"))

