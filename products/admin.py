from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import Category, Product, ProductImage, ProductVariant


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ["name", "display_name"]


class ProductVariantInline(TranslationTabularInline):
    model = ProductVariant
    extra = 0
    min_num = 1
    validate_min = True
    fields = [
        "name",
        "sku",
        "price",
        "sale_price",
        "stock",
        "personalization_max_length",
        "position",
        "is_active",
    ]


class ProductImageInline(TranslationTabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "variant", "position"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """In der Auswahl „Variante“ nur Varianten dieses Produkts zeigen."""
        if db_field.name == "variant":
            object_id = request.resolver_match.kwargs.get("object_id")
            kwargs["queryset"] = ProductVariant.objects.filter(product_id=object_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ["name", "category", "price", "stock", "is_active"]
    list_editable = ["price", "stock", "is_active"]
    list_filter = ["category", "is_active", "personalization_enabled"]
    search_fields = ["name", "sku", "description"]
    prepopulated_fields = {"slug": ["name_de"]}
    inlines = [ProductVariantInline, ProductImageInline]
