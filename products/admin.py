from django.contrib import admin
from django.utils.translation import gettext_lazy as _
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
        """In der Auswahl „Ausführung“ nur Varianten dieses Produkts zeigen."""
        if db_field.name == "variant":
            object_id = request.resolver_match.kwargs.get("object_id")
            kwargs["queryset"] = ProductVariant.objects.filter(product_id=object_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = [
        "name",
        "category",
        "price_from_display",
        "stock_total",
        "is_active",
    ]
    list_editable = ["is_active"]
    list_filter = ["category", "is_active", "personalization_enabled"]
    search_fields = ["name", "sku", "description"]
    prepopulated_fields = {"slug": ["name_de"]}
    inlines = [ProductVariantInline, ProductImageInline]
    fieldsets = [
        (_("Basics"), {"fields": ["name", "slug", "category", "sku", "is_active"]}),
        (_("Description and image"), {"fields": ["description", "image"]}),
        (
            _("Personalization"),
            {
                "fields": [
                    "personalization_enabled",
                    "personalization_required",
                    "personalization_label",
                    "personalization_help",
                ]
            },
        ),
        (
            _("Search engines (SEO)"),
            {"fields": ["meta_title", "meta_description"], "classes": ["collapse"]},
        ),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("variants")

    @admin.display(description=_("Price from"))
    def price_from_display(self, obj):
        return obj.price_from

    @admin.display(description=_("Stock"))
    def stock_total(self, obj):
        return sum(variant.stock for variant in obj.active_variants)
