from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .bag import Bag


def _get_quantity(request):
    """Menge aus dem Formular lesen, bei Unsinn 1."""
    try:
        return int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        return 1


def bag_detail(request):
    """Warenkorb-Seite. Die Zahlen kommen aus dem Context Processor."""
    return render(request, "bag/bag_detail.html")


@require_POST
def bag_add(request, product_id):
    """Produkt in den Warenkorb legen oder Menge erhöhen."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if not product.is_in_stock:
        messages.error(request, f"{product.name} ist leider ausverkauft.")
        return redirect(product.get_absolute_url())

    bag = Bag(request)
    wanted = bag.get_quantity(product) + max(_get_quantity(request), 1)
    bag.set_quantity(product, wanted)
    actual = bag.get_quantity(product)

    if actual < wanted:
        messages.warning(
            request,
            f"Nur {product.stock} Stück auf Lager. Im Warenkorb: {actual}.",
        )
    else:
        messages.success(request, f"{product.name} im Warenkorb: {actual} Stück.")
    return redirect(product.get_absolute_url())
