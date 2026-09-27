import hashlib
from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Tạo sẵn người dùng mẫu để kiểm thử đăng nhập và xác thực JWT'

    def handle(self, *args, **options):
        username = 'testuser'
        raw_pw = '123456'
        md5_pw = hashlib.md5(raw_pw.encode('utf-8')).hexdigest()

        user, created = User.objects.get_or_create(
            UserName=username,
            defaults={
                'Password': md5_pw,
                'Token': None
            }
        )

        if not created:
            user.Password = md5_pw
            user.save(update_fields=['Password'])
            self.stdout.write(self.style.SUCCESS(f"Tai khoan '{username}' da duoc cap nhat mat khau."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Tao thanh cong tai khoan mau: '{username}'."))

        self.stdout.write(self.style.NOTICE(f"  - UserName: {username}"))
        self.stdout.write(self.style.NOTICE(f"  - Mat khau goc: {raw_pw}"))
        self.stdout.write(self.style.NOTICE(f"  - Mat khau Base64: MTIzNDU2"))
        self.stdout.write(self.style.NOTICE(f"  - Mat khau MD5: {md5_pw}"))
