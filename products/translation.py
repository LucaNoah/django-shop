from modeltranslation.translator import TranslationOptions, register

from .models import Category, Product, ProductImage, ProductVariant


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("display_name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",
        "personalization_label",
        "personalization_help",
        "meta_title",
        "meta_description",
    )


@register(ProductVariant)
class ProductVariantTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(ProductImage)
class ProductImageTranslationOptions(TranslationOptions):
    fields = ("alt_text",)
