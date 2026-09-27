import base64
import datetime
import hashlib
import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password


def generate_jwt(user):
    """
    Sinh JWT token với payload tối ưu (độ dài ~140-160 ký tự)
    để vừa vặn với trường VARCHAR(255) của bảng User.
    Thời hạn token mặc định: 2 giờ.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        'id': user.IdUser,
        'username': user.UserName,
        'exp': now + datetime.timedelta(hours=2),
        'iat': now,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def decode_jwt(token):
    """
    Giải mã và kiểm tra tính hợp lệ của JWT token.
    Trả về tuple: (payload, error_message)
    """
    if not token:
        return None, "Token không được để trống."
    
    # Loại bỏ tiền tố 'Bearer ' nếu có
    if token.startswith("Bearer "):
        token = token[7:].strip()
    elif token.startswith("bearer "):
        token = token[7:].strip()
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token đã hết hạn (Expired)."
    except jwt.InvalidSignatureError:
        return None, "Chữ ký Token không hợp lệ (Invalid Signature)."
    except jwt.DecodeError:
        return None, "Cấu trúc Token không hợp lệ (Decode Error)."
    except jwt.InvalidTokenError as e:
        return None, f"Token không hợp lệ: {str(e)}"


def verify_password(input_password, stored_password):
    """
    Kiểm tra mật khẩu client gửi lên (có thể là Plain text, Base64 hoặc MD5)
    so với mật khẩu lưu trong cơ sở dữ liệu.
    """
    if not input_password or not stored_password:
        return False

    input_str = str(input_password).strip()
    stored_str = str(stored_password).strip()

    # 1. Trực tiếp so khớp (nếu DB lưu cùng dạng với client gửi)
    if input_str == stored_str:
        return True

    # 2. Trường hợp Client gửi MD5 (32 ký tự hex)
    # So sánh nếu stored là plain text và md5(stored) == input
    if hashlib.md5(stored_str.encode('utf-8')).hexdigest().lower() == input_str.lower():
        return True

    # Trường hợp DB lưu MD5 và client gửi plain text: md5(input) == stored
    if hashlib.md5(input_str.encode('utf-8')).hexdigest().lower() == stored_str.lower():
        return True

    # 3. Trường hợp Client gửi Base64
    try:
        decoded_bytes = base64.b64decode(input_str, validate=True)
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        if decoded_str:
            # So khớp decoded với stored
            if decoded_str == stored_str:
                return True
            # So khớp md5(decoded) với stored
            if hashlib.md5(decoded_str.encode('utf-8')).hexdigest().lower() == stored_str.lower():
                return True
            # So khớp md5(stored) với decoded
            if hashlib.md5(stored_str.encode('utf-8')).hexdigest().lower() == decoded_str.lower():
                return True
            # Kiểm tra Django hash nếu có
            try:
                if check_password(decoded_str, stored_str):
                    return True
            except Exception:
                pass
    except Exception:
        pass

    # 4. Kiểm tra mã hóa password mặc định của Django
    try:
        if check_password(input_str, stored_str):
            return True
    except Exception:
        pass

    return False
