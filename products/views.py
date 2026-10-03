from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product

# Erlaubte Sortierungen: Wert in der Adresse -> Feld in der Datenbank
SORT_OPTIONS = {
    "name": "name",
    "-name": "-name",
    "price": "price",
    "-price": "-price",
    "newest": "-created_at",
}


def product_list(request):
    """Aktive Produkte, optional durchsucht, gefiltert und sortiert."""
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()

    # Suche in Name und Beschreibung
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Filter nach Kategorie
    current_category = request.GET.get("category", "")
    if current_category:
        products = products.filter(category__name=current_category)

    # Sortierung, nur erlaubte Werte
    current_sort = request.GET.get("sort", "name")
    if current_sort not in SORT_OPTIONS:
        current_sort = "name"
    products = products.order_by(SORT_OPTIONS[current_sort])

    context = {
        "products": products,
        "categories": categories,
        "query": query,
        "current_category": current_category,
        "current_sort": current_sort,
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, slug):
    """Ein einzelnes Produkt, gefunden über seinen Slug."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "products/product_detail.html", {"product": product})
