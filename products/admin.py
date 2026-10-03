from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "display_name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "is_active"]
    list_editable = ["price", "stock", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "sku", "description"]
    prepopulated_fields = {"slug": ["name"]}