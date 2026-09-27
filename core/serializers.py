from rest_framework import serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    userName = serializers.CharField(
        required=True,
        help_text="Tên đăng nhập (hoặc email). Có thể dùng key 'userName' hoặc 'username'."
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Mật khẩu của người dùng (hỗ trợ plain text, Base64 hoặc mã băm MD5)."
    )

    def to_internal_value(self, data):
        # Hỗ trợ cả trường hợp client gửi userName / username, password / Password
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'username' in mutable_data and 'userName' not in mutable_data:
            mutable_data['userName'] = mutable_data['username']
        if 'Password' in mutable_data and 'password' not in mutable_data:
            mutable_data['password'] = mutable_data['Password']
        return super().to_internal_value(mutable_data)


class TokenCheckSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Chuỗi JWT token (nếu không truyền qua Header Authorization: Bearer <token>)"
    )


class RegisterSerializer(serializers.Serializer):
    userName = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255, write_only=True)


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['IdUser', 'UserName', 'Token']
