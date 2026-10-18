from django.urls import re_path
from .views import product_list_create_view, product_detail_update_delete_view

urlpatterns = [
    # Tuyến đường danh sách và tạo mới sản phẩm (hỗ trợ cả có và không có dấu '/' ở cuối)
    re_path(r'^products/?$', product_list_create_view, name='product_list_create'),
    
    # Tuyến đường chi tiết, cập nhật và xóa sản phẩm theo ID
    re_path(r'^products/(?P<pk>\d+)/?$', product_detail_update_delete_view, name='product_detail_update_delete'),
]
