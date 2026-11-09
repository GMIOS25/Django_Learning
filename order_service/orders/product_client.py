import logging
import sys
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ProductServiceClient:
    """
    Client giao tiếp liên dịch vụ (Inter-Service) giữa Order Service và Product Service.
    Tuân thủ nguyên tắc SOA: Order Service không truy cập trực tiếp DB của Product Service.
    """

    @classmethod
    def get_base_url(cls):
        return getattr(settings, 'PRODUCT_SERVICE_URL', 'http://127.0.0.1:8001/products').rstrip('/')

    @classmethod
    def get_timeout(cls):
        default_timeout = 0.1 if 'test' in sys.argv else 5
        return getattr(settings, 'PRODUCT_SERVICE_TIMEOUT', default_timeout)

    @classmethod
    def get_product(cls, product_id, token=None):
        """
        Gọi GET /products/<id> sang Product Service để lấy thông tin sản phẩm và số lượng tồn kho.
        Trả về: (product_data: dict, error_message: str)
        """
        base_url = cls.get_base_url()
        url = f"{base_url}/{product_id}"
        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"

        try:
            resp = requests.get(url, headers=headers, timeout=cls.get_timeout())
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data'], None
                return data, None
            elif resp.status_code == 404:
                return None, f"Sản phẩm với ID {product_id} không tồn tại trên hệ thống Product Service."
            elif resp.status_code == 401:
                return None, "Xác thực với Product Service thất bại (Token không hợp lệ hoặc đã hết hạn)."
            else:
                return None, f"Product Service phản hồi mã lỗi {resp.status_code}."
        except Exception as exc:
            logger.warning(f"Không thể kết nối tới Product Service ({url}): {exc}")
            return None, f"Không thể kết nối tới Product Service tại {url}."

    @classmethod
    def check_stock(cls, product_id, requested_quantity, token=None):
        """
        Kiểm tra số lượng sản phẩm tồn kho từ Product Service.
        Trả về: (is_available: bool, product_data: dict, error_message: str)
        """
        if requested_quantity <= 0:
            return False, None, "Số lượng đặt mua phải lớn hơn 0."

        product_data, err = cls.get_product(product_id, token=token)
        if err or not product_data:
            return False, None, err

        stock = product_data.get('quantity', 0)
        product_name = product_data.get('name', f"ID {product_id}")
        if stock < requested_quantity:
            return (
                False,
                product_data,
                f"Sản phẩm '{product_name}' (ID: {product_id}) không đủ tồn kho. Tồn kho hiện có: {stock}, số lượng yêu cầu: {requested_quantity}."
            )

        return True, product_data, None

    @classmethod
    def deduct_stock(cls, product_id, quantity, token=None):
        """
        Trừ số lượng tồn kho trên Product Service khi đơn hàng được tạo.
        """
        product_data, err = cls.get_product(product_id, token=token)
        if err or not product_data:
            return False, err

        current_stock = product_data.get('quantity', 0)
        new_stock = max(0, current_stock - quantity)

        base_url = cls.get_base_url()
        url = f"{base_url}/{product_id}"
        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"

        try:
            resp = requests.patch(
                url,
                json={'quantity': new_stock},
                headers=headers,
                timeout=cls.get_timeout()
            )
            if resp.status_code in (200, 204):
                return True, None
            return False, f"Không thể cập nhật tồn kho trên Product Service (Mã {resp.status_code})."
        except Exception as exc:
            logger.error(f"Lỗi khi trừ tồn kho Product Service ({url}): {exc}")
            return False, str(exc)

    @classmethod
    def restore_stock(cls, product_id, quantity, token=None):
        """
        Hoàn trả lại số lượng tồn kho trên Product Service khi đơn hàng bị hủy hoặc item bị xóa.
        """
        product_data, err = cls.get_product(product_id, token=token)
        if err or not product_data:
            return False, err

        current_stock = product_data.get('quantity', 0)
        new_stock = current_stock + quantity

        base_url = cls.get_base_url()
        url = f"{base_url}/{product_id}"
        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"

        try:
            resp = requests.patch(
                url,
                json={'quantity': new_stock},
                headers=headers,
                timeout=cls.get_timeout()
            )
            if resp.status_code in (200, 204):
                return True, None
            return False, f"Không thể hoàn tồn kho trên Product Service (Mã {resp.status_code})."
        except Exception as exc:
            logger.error(f"Lỗi khi hoàn tồn kho Product Service ({url}): {exc}")
            return False, str(exc)
