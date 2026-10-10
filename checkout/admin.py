from django.contrib import admin

from .models import Order, OrderLineItem


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0
    readonly_fields = ["lineitem_total"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderLineItemInline]
    list_display = [
        "order_number",
        "created_at",
        "full_name",
        "status",
        "language",
        "grand_total",
    ]
    list_filter = ["status", "language", "created_at"]
    search_fields = ["order_number", "full_name", "email"]
    readonly_fields = [
        "order_number",
        "created_at",
        "order_total",
        "delivery_cost",
        "grand_total",
        "stripe_session_id",
        "paid_at",
        "language",
    ]
