from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def service_info_view(request):
    """
    Endpoint thông tin dịch vụ báo cáo (SOA Reporting Service - Bài Thực Hành Số 5).
    """
    return JsonResponse({
        'service': 'Reporting Service',
        'description': 'Bài thực hành số 5 - Kiến trúc hướng dịch vụ (SOA)',
        'port': 8003,
        'status': 'running',
        'dependencies': {
            'auth_service': 'http://127.0.0.1:8000/auth (Bài thực hành số 2)',
            'product_service': 'http://127.0.0.1:8001/products (Bài thực hành số 3)',
            'order_service': 'http://127.0.0.1:8002/orders (Bài thực hành số 4)',
        },
        'endpoints': {
            'get_product_reports': 'GET /reports/products',
            'get_product_report_detail': 'GET /reports/products/<id>',
            'create_product_report': 'POST /reports/products',
            'delete_product_report': 'DELETE /reports/products/<id>',
            'get_order_reports': 'GET /reports/orders',
            'get_order_report_detail': 'GET /reports/orders/<id>',
            'create_order_report': 'POST /reports/orders',
            'delete_order_report': 'DELETE /reports/orders/<id>',
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
    path('', include('reports.urls')),
    path('api/', include('reports.urls')),
]

