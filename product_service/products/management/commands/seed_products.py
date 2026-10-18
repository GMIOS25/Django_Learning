import sys
from decimal import Decimal
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Tao du lieu san pham mau phuc vu kiem thu cho Bai Thuc Hanh So 3'

    def handle(self, *args, **options):
        # Configure stdout for safe output on Windows cmd/powershell
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass

        sample_products = [
            {
                "name": "Laptop Dell XPS 15 9530",
                "description": "Intel Core i7-13700H, 16GB RAM, 512GB SSD, RTX 4050, 15.6 inch OLED 3.5K Touch.",
                "price": Decimal("42500000.00"),
                "quantity": 10
            },
            {
                "name": "Ban phim co khong day Keychron Q1 Pro",
                "description": "Custom Mechanical Keyboard 75%, vo nhom CNC nguyen khoi, ket noi Bluetooth 5.1 va Type-C.",
                "price": Decimal("4850000.00"),
                "quantity": 25
            },
            {
                "name": "Chuot cong thai hoc Logitech MX Master 3S",
                "description": "Cam bien 8000 DPI Darkfield, con lan co hoc MagSpeed, ket noi da thiet bi Flow.",
                "price": Decimal("2290000.00"),
                "quantity": 40
            },
            {
                "name": "Tai nghe chong on Sony WH-1000XM5",
                "description": "Chong on chu dong hang dau nganh ANC, bo giai ma am thanh Hi-Res LDAC, thoi luong pin 30 gio.",
                "price": Decimal("6990000.00"),
                "quantity": 15
            },
            {
                "name": "Man hinh Dell UltraSharp U2723QE 27 inch 4K",
                "description": "Tam nen IPS Black do tuong phan 2000:1, 98% DCI-P3, tich hop cong sac Type-C 90W va Hub USB.",
                "price": Decimal("12900000.00"),
                "quantity": 8
            }
        ]

        created_count = 0
        for item in sample_products:
            obj, created = Product.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "price": item["price"],
                    "quantity": item["quantity"]
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"[CREATED] ID {obj.id}: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"[EXISTS]  ID {obj.id}: {obj.name}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nHoan tat! Da them moi {created_count} san pham. Tong so san pham hien co: {Product.objects.count()}"
        ))
