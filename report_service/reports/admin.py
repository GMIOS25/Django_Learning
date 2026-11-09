from django.contrib import admin
from .models import OrderReport, ProductReport


class ProductReportInline(admin.TabularInline):
    model = ProductReport
    extra = 0
    fields = ['product_id', 'total_sold', 'revenue', 'cost', 'profit']
    readonly_fields = ['profit', 'created_at', 'updated_at']


@admin.register(OrderReport)
class OrderReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'total_revenue', 'total_cost', 'total_profit', 'created_at']
    search_fields = ['order_id', 'id']
    readonly_fields = ['total_profit', 'created_at', 'updated_at']
    inlines = [ProductReportInline]


@admin.register(ProductReport)
class ProductReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_report', 'product_id', 'total_sold', 'revenue', 'cost', 'profit', 'created_at']
    list_filter = ['product_id']
    search_fields = ['product_id', 'id']
    readonly_fields = ['profit', 'created_at', 'updated_at']

