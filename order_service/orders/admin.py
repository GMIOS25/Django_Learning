from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product_id', 'product_name', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'id']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_id', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['product_id']
    search_fields = ['product_name', 'order__id', 'order__customer_name']
    readonly_fields = ['total_price']

