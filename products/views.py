from django.db.models import Min, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Category, Product

# Erlaubte Sortierungen: Wert in der Adresse -> Feld in der Datenbank
SORT_OPTIONS = {
    "name": "name",
    "-name": "-name",
    "price": "min_price",
    "-price": "-min_price",
    "newest": "-created_at",
}


def product_list(request):
    """Aktive Produkte mit mindestens einer aktiven Variante."""
    products = (
        Product.objects.filter(is_active=True)
        .annotate(min_price=Min("variants__price", filter=Q(variants__is_active=True)))
        .filter(min_price__isnull=False)
        .select_related("category")
        .prefetch_related("variants", "images")
    )
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
    """Ein Produkt mit wählbarer Ausführung, passenden Bildern und Personalisierung."""
    product = get_object_or_404(
        Product.objects.prefetch_related("variants", "images"),
        slug=slug,
        is_active=True,
    )
    variants = product.active_variants
    if not variants:
        raise Http404

    # Gewählte Ausführung aus der Adresse (?variant=12), sonst die erste lieferbare
    selected_variant = None
    requested = request.GET.get("variant")
    if requested:
        selected_variant = next((v for v in variants if str(v.id) == requested), None)
    if selected_variant is None:
        selected_variant = next((v for v in variants if v.is_in_stock), variants[0])

    # Bilder: zuerst die der Ausführung, dann die gemeinsamen, zuletzt das Hauptbild
    all_images = list(product.images.all())
    pictures = [img for img in all_images if img.variant_id == selected_variant.id]
    pictures += [img for img in all_images if img.variant_id is None]
    gallery = [
        {"url": img.image.url, "alt": img.alt_text or product.name} for img in pictures
    ]
    if product.image:
        gallery.append({"url": product.image.url, "alt": product.name})

    context = {
        "product": product,
        "variants": variants,
        "selected_variant": selected_variant,
        "show_variant_select": len(variants) > 1,
        "gallery": gallery,
    }
    return render(request, "products/product_detail.html", context)
