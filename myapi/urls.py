from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import login_view, auth_view, hello_world, register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Tuyến đường OpenAPI & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),

    # Các tuyến đường API chuẩn DRF
    path('api/', include('core.urls')),

    # Hỗ trợ URL trực tiếp (hỗ trợ cả có và không có dấu '/' ở cuối mà không bị 301 redirect)
    # Url login: localhost:****/ và /login
    path('', login_view, name='root_login'),
    re_path(r'^login/?$', login_view, name='login_shortcut'),
    
    # Url auth: localhost:****/auth
    re_path(r'^auth/?$', auth_view, name='auth_shortcut'),
    
    # Url hello world ở bài thực hành số 1
    re_path(r'^hello/?$', hello_world, name='hello_shortcut'),
    re_path(r'^register/?$', register_view, name='register_shortcut'),
]
