from modeltranslation.translator import TranslationOptions, register

from .models import Category, Product, ProductImage


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("display_name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(ProductImage)
class ProductImageTranslationOptions(TranslationOptions):
    fields = ("alt_text",)
