import logging
import sys
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OrderServiceClient:
    """
    Client giao tiếp liên dịch vụ với Order Service (cổng 8002).
    """

    @classmethod
    def get_base_url(cls):
        return getattr(settings, 'ORDER_SERVICE_URL', 'http://127.0.0.1:8002/orders').rstrip('/')

    @classmethod
    def get_timeout(cls):
        default_timeout = 0.1 if 'test' in sys.argv else 5
        return getattr(settings, 'ORDER_SERVICE_TIMEOUT', default_timeout)

    @classmethod
    def get_order(cls, order_id, token=None):
        """
        Gọi GET /orders/<id> sang Order Service để lấy thông tin đơn hàng và chi tiết mặt hàng.
        Trả về: (order_data: dict, error_message: str)
        """
        base_url = cls.get_base_url()
        url = f"{base_url}/{order_id}"
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
                return None, f"Không tìm thấy đơn hàng với ID {order_id} trên Order Service."
            elif resp.status_code == 401:
                return None, "Xác thực với Order Service thất bại (Token không hợp lệ hoặc đã hết hạn)."
            else:
                return None, f"Order Service phản hồi mã lỗi {resp.status_code}."
        except Exception as exc:
            logger.warning(f"Không thể kết nối tới Order Service ({url}): {exc}")
            return None, f"Không thể kết nối tới Order Service tại {url}."

    @classmethod
    def get_orders(cls, token=None):
        """
        Gọi GET /orders sang Order Service để lấy toàn bộ danh sách đơn hàng.
        """
        base_url = cls.get_base_url()
        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"

        try:
            resp = requests.get(base_url, headers=headers, timeout=cls.get_timeout())
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data'], None
                return data, None
            return None, f"Order Service phản hồi mã lỗi {resp.status_code}."
        except Exception as exc:
            logger.warning(f"Không thể kết nối tới Order Service ({base_url}): {exc}")
            return None, f"Không thể kết nối tới Order Service tại {base_url}."


class ProductServiceClient:
    """
    Client giao tiếp liên dịch vụ với Product Service (cổng 8001).
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
        Gọi GET /products/<id> sang Product Service để lấy thông tin sản phẩm.
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
                return None, f"Không tìm thấy sản phẩm với ID {product_id} trên Product Service."
            elif resp.status_code == 401:
                return None, "Xác thực với Product Service thất bại."
            else:
                return None, f"Product Service phản hồi mã lỗi {resp.status_code}."
        except Exception as exc:
            logger.warning(f"Không thể kết nối tới Product Service ({url}): {exc}")
            return None, f"Không thể kết nối tới Product Service tại {url}."

    @classmethod
    def get_products(cls, token=None):
        """
        Gọi GET /products sang Product Service để lấy toàn bộ danh sách sản phẩm.
        """
        base_url = cls.get_base_url()
        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"

        try:
            resp = requests.get(base_url, headers=headers, timeout=cls.get_timeout())
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data'], None
                return data, None
            return None, f"Product Service phản hồi mã lỗi {resp.status_code}."
        except Exception as exc:
            logger.warning(f"Không thể kết nối tới Product Service ({base_url}): {exc}")
            return None, f"Không thể kết nối tới Product Service tại {base_url}."

