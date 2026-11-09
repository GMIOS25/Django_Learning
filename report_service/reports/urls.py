from django.urls import re_path
from .views import (
    order_reports_list_create_view,
    order_reports_detail_delete_view,
    product_reports_list_create_view,
    product_reports_detail_delete_view,
)

urlpatterns = [
    re_path(r'^reports/orders/?$', order_reports_list_create_view, name='order_reports_list_create'),
    re_path(r'^reports/orders/(?P<pk>\d+)/?$', order_reports_detail_delete_view, name='order_reports_detail_delete'),
    re_path(r'^reports/products/?$', product_reports_list_create_view, name='product_reports_list_create'),
    re_path(r'^reports/products/(?P<pk>\d+)/?$', product_reports_detail_delete_view, name='product_reports_detail_delete'),
]
