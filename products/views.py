from django.shortcuts import get_object_or_404, render

from .models import Product


def product_list(request):
    """Alle aktiven Produkte."""
    products = Product.objects.filter(is_active=True).select_related("category")
    return render(request, "products/product_list.html", {"products": products})


def product_detail(request, slug):
    """Ein einzelnes Produkt, gefunden über seinen Slug."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "products/product_detail.html", {"product": product})