from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
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
        messages.error(
            request,
            _("%(name)s is unfortunately sold out.") % {"name": product.name},
        )
        return redirect(product.get_absolute_url())

    bag = Bag(request)
    wanted = bag.get_quantity(product) + max(_get_quantity(request), 1)
    bag.set_quantity(product, wanted)
    actual = bag.get_quantity(product)

    if actual < wanted:
        messages.warning(
            request,
            _("Only %(stock)s in stock. In your shopping bag: %(quantity)s.")
            % {"stock": product.stock, "quantity": actual},
        )
    else:
        messages.success(
            request,
            _("%(name)s in your shopping bag: %(quantity)s.")
            % {"name": product.name, "quantity": actual},
        )
    return redirect(product.get_absolute_url())


@require_POST
def bag_update(request, product_id):
    """Menge im Warenkorb ändern. 0 entfernt das Produkt."""
    product = get_object_or_404(Product, id=product_id)
    bag = Bag(request)
    wanted = _get_quantity(request)
    bag.set_quantity(product, wanted)
    actual = bag.get_quantity(product)

    if actual == 0:
        messages.success(
            request,
            _("%(name)s was removed from your shopping bag.") % {"name": product.name},
        )
    elif actual < wanted:
        messages.warning(
            request,
            _("Only %(stock)s in stock. Quantity set to %(quantity)s.")
            % {"stock": product.stock, "quantity": actual},
        )
    else:
        messages.success(
            request,
            _("Quantity of %(name)s changed to %(quantity)s.")
            % {"name": product.name, "quantity": actual},
        )
    return redirect("bag:detail")


@require_POST
def bag_remove(request, product_id):
    """Produkt komplett aus dem Warenkorb nehmen."""
    product = get_object_or_404(Product, id=product_id)
    Bag(request).remove(product)
    messages.success(
        request,
        _("%(name)s was removed from your shopping bag.") % {"name": product.name},
    )
    return redirect("bag:detail")
