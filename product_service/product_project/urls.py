from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def service_info_view(request):
    """
    Endpoint thông tin dịch vụ quản lý sản phẩm (SOA Product Service).
    """
    return JsonResponse({
        "service": "Product Management Service",
        "description": "Bài thực hành số 3 - Kiến trúc hướng dịch vụ (SOA)",
        "port": 8001,
        "status": "running",
        "auth_service_dependency": "http://127.0.0.1:8000/ (Bài thực hành số 2)",
        "endpoints": {
            "get_all_products": "GET /products",
            "get_product_detail": "GET /products/<id>",
            "create_product": "POST /products",
            "update_product": "PUT /products/<id>",
            "delete_product": "DELETE /products/<id>",
            "swagger_docs": "/swagger/",
            "openapi_schema": "/api/schema/",
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OpenAPI & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),

    # Route gốc hiển thị thông tin service
    path('', service_info_view, name='service_info'),

    # Các tuyến đường API quản lý sản phẩm
    path('', include('products.urls')),
    path('api/', include('products.urls')),
]
