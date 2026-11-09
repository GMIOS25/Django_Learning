from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def service_info_view(request):
    """
    Endpoint thông tin dịch vụ quản lý đơn hàng (SOA Order Service - Bài Thực Hành Số 4).
    """
    return JsonResponse({
        'service': 'Order Management Service',
        'description': 'Bài thực hành số 4 - Kiến trúc hướng dịch vụ (SOA)',
        'port': 8002,
        'status': 'running',
        'dependencies': {
            'auth_service': 'http://127.0.0.1:8000/auth (Bài thực hành số 2)',
            'product_service': 'http://127.0.0.1:8001/products (Bài thực hành số 3)',
        },
        'endpoints': {
            'get_all_orders': 'GET /orders',
            'get_order_detail': 'GET /orders/<id>',
            'create_order': 'POST /orders',
            'update_order_status': 'PUT /orders/<id>',
            'delete_order': 'DELETE /orders/<id>',
            'get_all_order_items': 'GET /order_items',
            'get_order_item_detail': 'GET /order_items/<id>',
            'create_order_item': 'POST /order_items',
            'update_order_item': 'PUT /order_items/<id>',
            'delete_order_item': 'DELETE /order_items/<id>',
            'swagger_docs': '/swagger/',
            'openapi_schema': '/api/schema/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('', service_info_view, name='service_info'),
    path('', include('orders.urls')),
    path('api/', include('orders.urls')),
]
