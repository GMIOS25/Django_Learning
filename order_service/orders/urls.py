from django.urls import re_path
from .views import (
    order_list_create_view,
    order_detail_update_delete_view,
    order_item_list_create_view,
    order_item_detail_update_delete_view,
)

urlpatterns = [
    re_path(r'^orders/?$', order_list_create_view, name='order_list_create'),
    re_path(r'^orders/(?P<pk>\d+)/?$', order_detail_update_delete_view, name='order_detail_update_delete'),
    re_path(r'^order_items/?$', order_item_list_create_view, name='order_item_list_create'),
    re_path(r'^order_items/(?P<pk>\d+)/?$', order_item_detail_update_delete_view, name='order_item_detail_update_delete'),
]

